import pytest
from django.urls import reverse
from campaigns.models import Campaign, Contribution

pytestmark = pytest.mark.django_db
PANEL = reverse("creator_panel")


def test_ca1_only_own_campaigns_with_drafts_and_data(client, campaign_factory, owner, other):
    activa = campaign_factory(title="Proyecto solar")
    borrador = campaign_factory(title="Huerto urbano", status=Campaign.Status.BORRADOR)
    ajena = campaign_factory(title="Campaña ajena", creator=other)
    Contribution.objects.create(campaign=activa, user=other, amount=350)

    client.force_login(owner)
    response = client.get(PANEL)
    text = response.content.decode()

    assert response.status_code == 200
    assert activa.title in text and borrador.title in text
    assert ajena.title not in text
    for value in ["Activa", "Borrador", "350.00", "1000.00"]:
        assert value in text


def test_ca2_view_edit_delete_links(client, campaign_factory, owner):
    c = campaign_factory()
    client.force_login(owner)
    text = client.get(PANEL).content.decode()

    for name in ["campaign_detail", "campaign_edit", "campaign_delete"]:
        assert reverse(name, args=[c.pk]) in text
    for label in ["Ver", "Editar", "Eliminar"]:
        assert label in text


def test_ca3_empty_panel_message_and_create_button(client, owner):
    client.force_login(owner)
    text = client.get(PANEL).content.decode()

    create_url = reverse("campaign_create")
    assert "Aún no has creado campañas" in text
    assert f'<a href="{create_url}" class="btn btn-primary">Crear campaña</a>' in text
    assert text.count(f'href="{create_url}"') == 2


def test_ca4_anonymous_redirected_to_login(client):
    response = client.get(PANEL)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_navbar_campaign_panel_button(client, owner):
    HOME = reverse("home")
    text = client.get(HOME).content.decode()
    
    assert "Panel de campañas" not in text
    assert reverse("creator_panel") not in text
    
    client.force_login(owner)
    text = client.get(HOME).content.decode()
    
    assert "Panel de campañas" in text
    assert reverse("creator_panel") in text