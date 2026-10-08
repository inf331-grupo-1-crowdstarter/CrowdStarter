import pytest
from django.urls import reverse
from campaigns.models import Contribution
pytestmark = pytest.mark.django_db

def test_ca1_full_detail(client, campaign_factory, other):
    c = campaign_factory()
    Contribution.objects.create(campaign=c, user=other, amount=350)
    text = client.get(c.get_absolute_url()).content.decode()
    for value in [c.title, c.description, c.category.name, "Activa", "1000", "350", "35.0%", c.deadline.strftime("%d/%m/%Y"), c.creator.username, c.image_url]:
        assert value in text

def test_ca2_missing_404(client):
    assert client.get(reverse("campaign_detail", args=[999])).status_code == 404

def test_ca3_draft_only_owner(client, campaign_factory, owner, other):
    c = campaign_factory(status="BORRADOR")
    assert client.get(c.get_absolute_url()).status_code == 404
    client.force_login(other)
    assert client.get(c.get_absolute_url()).status_code == 404
    client.force_login(owner)
    assert client.get(c.get_absolute_url()).status_code == 200

def test_ca4_owner_options(client, campaign_factory, owner, other):
    c = campaign_factory()
    for user in [other, owner]:
        client.force_login(user)
        text = client.get(c.get_absolute_url()).content.decode()
        assert ("Editar" in text) == (user == owner)
        assert ("Eliminar" in text) == (user == owner)

@pytest.mark.parametrize("image", ["", "campaigns/missing.jpg", "campaigns/broken.png"])
def test_ca5_invalid_image_fallback(client, campaign_factory, settings, tmp_path, image):
    settings.MEDIA_ROOT = tmp_path
    if image.endswith("broken.png"):
        (tmp_path/"campaigns").mkdir()
        (tmp_path/image).write_bytes(b"invalid image")
    c = campaign_factory(image=image)
    assert '/static/campaigns/default.svg' in client.get(c.get_absolute_url()).content.decode()
