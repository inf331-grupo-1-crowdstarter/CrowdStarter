import pytest
from django.urls import reverse
from campaigns.models import Contribution
pytestmark = pytest.mark.django_db

def test_ca1_ca2_ca4_recent_first_ten_and_pagination(client, campaign_factory):
    rows = [campaign_factory(title=f"Campaña {i}") for i in range(12)]
    response = client.get(reverse("campaign_list"))
    assert list(response.context["page_obj"]) == list(reversed(rows))[:10]
    assert b"Siguiente" in response.content
    assert list(client.get(reverse("campaign_list"), {"page": 2}).context["page_obj"]) == [rows[1], rows[0]]

def test_ca3_ca7_card_fields_and_detail_link(client, campaign_factory, other):
    c = campaign_factory()
    Contribution.objects.create(campaign=c, user=other, amount=250)
    text = client.get(reverse("campaign_list")).content.decode()
    for value in [c.title, str(c.category), "Activa", "1000", "25.0%", c.deadline.strftime("%d/%m/%Y"), c.image_url, c.get_absolute_url()]:
        assert value in text
    assert client.get(c.get_absolute_url()).status_code == 200

def test_ca5_ca6_empty_and_draft_hidden(client, campaign_factory):
    campaign_factory(status="BORRADOR", title="Secreto")
    response = client.get(reverse("campaign_list"))
    assert "No hay campañas disponibles." in response.content.decode()
    assert "Secreto" not in response.content.decode()
