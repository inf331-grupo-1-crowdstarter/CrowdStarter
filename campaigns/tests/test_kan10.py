from datetime import timedelta
import pytest
from django.urls import reverse
from django.utils import timezone
from campaigns.models import Category, Contribution
pytestmark = pytest.mark.django_db

def url(c): return reverse("campaign_edit", args=[c.pk])

def test_ca1_prefilled(client, owner, campaign_factory):
    c = campaign_factory(); client.force_login(owner)
    form = client.get(url(c)).context["form"]
    assert form.instance == c
    for field in ["title", "description", "funding_goal", "deadline"]:
        assert str(form[field].value()) == str(getattr(c, field))
    assert form["category"].value() == c.category_id

def test_ca2_all_editable_fields(client, owner, campaign_factory, valid_data, image_file):
    c = campaign_factory(); client.force_login(owner)
    cat = Category.objects.create(name="Arte")
    data = dict(valid_data, category=cat.pk, image=image_file())
    assert client.post(url(c), data).status_code == 302
    c.refresh_from_db()
    for field in ["title", "description", "deadline"]: assert str(getattr(c, field)) == str(data[field])
    assert c.category == cat and c.funding_goal == 1500 and c.image.name
    assert c.creator == owner

@pytest.mark.parametrize("method", ["get", "post"])
def test_ca3_nonowner_forbidden(client, other, campaign_factory, valid_data, method):
    c = campaign_factory(); client.force_login(other)
    assert getattr(client, method)(url(c), valid_data).status_code == 404
    c.refresh_from_db(); assert c.title == "Proyecto solar"

def test_ca4_anonymous_login(client, campaign_factory):
    c = campaign_factory()
    assert client.get(url(c)).url == reverse("login")+"?next="+url(c)

@pytest.mark.parametrize("offset,ok", [(-1, False), (0, True), (1, True)])
def test_ca5_deadline_boundary(client, owner, campaign_factory, valid_data, offset, ok):
    c = campaign_factory(); client.force_login(owner)
    data = dict(valid_data, deadline=str(timezone.localdate()+timedelta(days=offset)))
    r = client.post(url(c), data)
    assert (r.status_code == 302) == ok
    if not ok: assert "deadline" in r.context["form"].errors

@pytest.mark.parametrize("amount,ok", [("0", False), ("-2", False), ("199.99", False), ("200", True)])
def test_ca6_goal_positive_at_least_raised(client, owner, other, campaign_factory, valid_data, amount, ok):
    c = campaign_factory(); Contribution.objects.create(campaign=c, user=other, amount=200)
    client.force_login(owner)
    r = client.post(url(c), dict(valid_data, funding_goal=amount))
    assert (r.status_code == 302) == ok
    c.refresh_from_db()
    if ok: assert c.status == "FINANCIADA"
    else:
        assert "funding_goal" in r.context["form"].errors
        assert c.funding_goal == 1000

def test_ca7_keep_existing_image(client, owner, campaign_factory, valid_data, image_file):
    c = campaign_factory(image=image_file()); name = c.image.name
    client.force_login(owner)
    assert client.post(url(c), valid_data).status_code == 302
    c.refresh_from_db(); assert c.image.name == name and c.image.storage.exists(name)

def test_ca8_retain_invalid_submission(client, owner, campaign_factory, valid_data):
    c = campaign_factory(); client.force_login(owner)
    r = client.post(url(c), dict(valid_data, funding_goal="0"))
    assert r.context["form"]["title"].value() == valid_data["title"]
    assert r.context["form"]["funding_goal"].value() == "0"
    c.refresh_from_db(); assert c.title == "Proyecto solar"

@pytest.mark.parametrize("status", ["FINANCIADA", "NO_FINANCIADA"])
def test_ca9_closed_not_editable(client, owner, campaign_factory, valid_data, status):
    c = campaign_factory(status=status); client.force_login(owner)
    assert client.get(url(c)).status_code == 403
    assert client.post(url(c), valid_data).status_code == 403
    c.refresh_from_db(); assert c.title == "Proyecto solar"
