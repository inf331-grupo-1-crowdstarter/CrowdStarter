import pytest
from django.urls import reverse
from django.test import Client
from campaigns.models import Campaign, Contribution
pytestmark = pytest.mark.django_db

def url(c): return reverse("campaign_delete", args=[c.pk])

def test_ca1_confirmation_get_does_not_delete(client, owner, campaign_factory):
    c = campaign_factory(); client.force_login(owner)
    r = client.get(url(c))
    assert r.status_code == 200 and "Confirmar eliminación" in r.content.decode()
    assert Campaign.objects.filter(pk=c.pk).exists()

def test_ca2_ca6_confirm_deletes_success_and_detail_404(client, owner, campaign_factory):
    c = campaign_factory(); client.force_login(owner); detail = c.get_absolute_url()
    r = client.post(url(c), follow=True)
    assert "Campaña eliminada correctamente" in r.content.decode()
    assert not Campaign.objects.filter(pk=c.pk).exists()
    assert client.get(detail).status_code == 404

def test_ca3_cancel_keeps_campaign(client, owner, campaign_factory):
    c = campaign_factory(); client.force_login(owner)
    assert f'href="{c.get_absolute_url()}">Cancelar' in client.get(url(c)).content.decode()
    assert client.get(c.get_absolute_url()).status_code == 200
    assert Campaign.objects.filter(pk=c.pk).exists()

@pytest.mark.parametrize("method", ["get", "post"])
def test_ca4_nonowner_cannot_delete(client, other, campaign_factory, method):
    c = campaign_factory(); client.force_login(other)
    assert getattr(client, method)(url(c)).status_code == 404
    assert Campaign.objects.filter(pk=c.pk).exists()

def test_ca5_anonymous_login(client, campaign_factory):
    c = campaign_factory()
    for r in [client.get(url(c)), client.post(url(c))]:
        assert r.status_code == 302 and r.url == reverse("login")+"?next="+url(c)
    assert Campaign.objects.filter(pk=c.pk).exists()

def test_ca7_contributions_prevent_deletion(client, owner, other, campaign_factory):
    c = campaign_factory(); Contribution.objects.create(campaign=c, user=other, amount=5)
    client.force_login(owner)
    assert "No puedes eliminar" in client.get(url(c)).content.decode()
    assert client.post(url(c)).status_code == 403
    assert Campaign.objects.filter(pk=c.pk).exists() and Contribution.objects.count() == 1

def test_delete_csrf_required(owner, campaign_factory):
    c = campaign_factory(); client = Client(enforce_csrf_checks=True); client.force_login(owner)
    assert client.post(url(c)).status_code == 403
    assert Campaign.objects.filter(pk=c.pk).exists()
