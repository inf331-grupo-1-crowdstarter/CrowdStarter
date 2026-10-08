from datetime import timedelta
from decimal import Decimal
import pytest
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from campaigns.models import Campaign, Contribution
pytestmark = pytest.mark.django_db

def url(c): return reverse("campaign_contribute", args=[c.pk])

def test_ca1_active_authenticated_option_and_amount(client, other, campaign_factory):
    c = campaign_factory(); client.force_login(other)
    text = client.get(c.get_absolute_url()).content.decode()
    assert 'name="amount"' in text and 'Aportar</button>' in text and "Pago simulado" in text

def test_ca2_positive_persisted_and_calculated_progress(client, other, campaign_factory):
    c = campaign_factory(); client.force_login(other)
    r = client.post(url(c), {"amount": "125.50", "user": c.creator_id}, follow=True)
    contribution = Contribution.objects.get()
    assert contribution.user == other and contribution.campaign == c and contribution.amount == Decimal("125.50")
    assert c.raised_amount == Decimal("125.50") and c.progress == Decimal("12.55")
    assert "Aporte simulado registrado" in r.content.decode()
    assert "125.50" in r.content.decode() and "12.6%" in r.content.decode()

@pytest.mark.parametrize("amount", ["", "0", "-1", "abc", "NaN", "Infinity", "0.001", "10000000000.00"])
def test_ca3_invalid_no_contribution(client, other, campaign_factory, amount):
    c = campaign_factory(); client.force_login(other)
    r = client.post(url(c), {"amount": amount})
    assert r.status_code == 200 and "amount" in r.context["contribution_form"].errors
    assert Contribution.objects.count() == 0
    c.refresh_from_db(); assert c.status == "ACTIVA" and c.raised_amount == 0

def test_ca4_login_and_return_to_campaign(client, other, campaign_factory):
    c = campaign_factory()
    r = client.post(url(c), {"amount": "10"})
    assert r.status_code == 302 and r.url == reverse("login")+"?next="+c.get_absolute_url()
    login_page = client.get(r.url)
    assert login_page.context["next"] == c.get_absolute_url()
    r = client.post(reverse("login"), {"username": other.username, "password": "ClaveSegura123!", "next": c.get_absolute_url()})
    assert r.url == c.get_absolute_url() and client.get(r.url).status_code == 200
    assert Contribution.objects.count() == 0

@pytest.mark.parametrize("status,expired", [("BORRADOR", False), ("FINANCIADA", False), ("NO_FINANCIADA", False), ("ACTIVA", True)])
def test_ca5_inactive_or_expired_rejected(client, other, campaign_factory, status, expired):
    kwargs = {"status": status}
    if expired: kwargs["deadline"] = timezone.localdate()-timedelta(days=1)
    c = campaign_factory(**kwargs); client.force_login(other)
    assert client.post(url(c), {"amount": "10"}).status_code == (404 if status == "BORRADOR" else 403)
    assert Contribution.objects.count() == 0
    assert 'name="amount"' not in client.get(c.get_absolute_url()).content.decode()
    if expired:
        c.refresh_from_db(); assert c.status == "NO_FINANCIADA"

def test_ca5_deadline_today_accepts(client, other, campaign_factory):
    c = campaign_factory(deadline=timezone.localdate()); client.force_login(other)
    assert client.post(url(c), {"amount": "1"}).status_code == 302
    assert Contribution.objects.count() == 1

def test_ca6_owner_rejected_and_no_option(client, owner, campaign_factory):
    c = campaign_factory(); client.force_login(owner)
    assert 'name="amount"' not in client.get(c.get_absolute_url()).content.decode()
    assert client.post(url(c), {"amount": "10"}).status_code == 403
    assert Contribution.objects.count() == 0

@pytest.mark.parametrize("last", ["900", "950"])
def test_ca7_total_reaches_or_exceeds_goal_closes_campaign(client, other, campaign_factory, last):
    c = campaign_factory(); client.force_login(other)
    assert client.post(url(c), {"amount": "100"}).status_code == 302
    c.refresh_from_db(); assert c.status == "ACTIVA"
    assert client.post(url(c), {"amount": last}).status_code == 302
    c.refresh_from_db(); assert c.status == "FINANCIADA" and c.raised_amount == 100+Decimal(last)
    assert client.post(url(c), {"amount": "1"}).status_code == 403
    assert Contribution.objects.count() == 2

def test_contribute_post_and_csrf_required(other, campaign_factory):
    c = campaign_factory(); client = Client(enforce_csrf_checks=True); client.force_login(other)
    assert client.get(url(c)).status_code == 405
    assert client.post(url(c), {"amount": "10"}).status_code == 403
    assert Contribution.objects.count() == 0

def test_complete_mvp_flow(client, owner, other, valid_data):
    client.force_login(owner)
    created = client.post(reverse("campaign_create"), valid_data)
    c = Campaign.objects.get(); assert created.url == c.get_absolute_url() and c.status == "BORRADOR"
    assert client.post(reverse("campaign_publish", args=[c.pk])).status_code == 302
    assert c.title in client.get(reverse("campaign_list"), {"q": c.title}).content.decode()
    client.force_login(other)
    assert client.post(url(c), {"amount": "1500"}).status_code == 302
    c.refresh_from_db(); assert c.status == "FINANCIADA"
    client.force_login(owner)
    assert client.post(reverse("campaign_edit", args=[c.pk]), valid_data).status_code == 403
    assert client.post(reverse("campaign_delete", args=[c.pk])).status_code == 403


@pytest.mark.parametrize("action", ["campaign_create", "campaign_edit", "campaign_publish"])
def test_shared_forms_csrf_required(owner, campaign_factory, valid_data, action):
    c = campaign_factory(status="BORRADOR")
    client = Client(enforce_csrf_checks=True); client.force_login(owner)
    target = reverse(action) if action == "campaign_create" else reverse(action, args=[c.pk])
    assert client.post(target, valid_data).status_code == 403
    c.refresh_from_db(); assert c.status == "BORRADOR" and c.title == "Proyecto solar"
    assert Campaign.objects.count() == 1

def test_valid_image_display_and_creation_boundaries(client, owner, valid_data, image_file):
    client.force_login(owner)
    data = dict(valid_data, title="x"*120, deadline=str(timezone.localdate()), image=image_file())
    r = client.post(reverse("campaign_create"), data)
    assert "deadline" in r.context["form"].errors and not Campaign.objects.exists()
    data["deadline"] = valid_data["deadline"]; data["image"] = image_file()
    assert client.post(reverse("campaign_create"), data).status_code == 302
    c = Campaign.objects.get()
    assert c.image.url in client.get(c.get_absolute_url()).content.decode()
    assert c.title == "x"*120

def test_expired_draft_cannot_be_published(client, owner, campaign_factory):
    c = campaign_factory(status="BORRADOR", deadline=timezone.localdate()-timedelta(days=1))
    client.force_login(owner)
    assert client.post(reverse("campaign_publish", args=[c.pk])).status_code == 403
    c.refresh_from_db(); assert c.status == "BORRADOR"
