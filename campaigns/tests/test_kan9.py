from datetime import timedelta
import pytest
from django.urls import reverse
from django.utils import timezone
from campaigns.models import Campaign
pytestmark = pytest.mark.django_db

def test_ca1_authenticated_form_fields(client, owner):
    client.force_login(owner)
    r = client.get(reverse("campaign_create"))
    assert r.status_code == 200
    assert set(r.context["form"].fields) == {"title", "description", "category", "image", "funding_goal", "deadline"}

def test_ca2_anonymous_login(client):
    url = reverse("campaign_create")
    for r in [client.get(url), client.post(url, {})]:
        assert r.status_code == 302 and r.url == reverse("login")+"?next="+url

def test_ca3_valid_creates_owned_draft_and_success(client, owner, valid_data, image_file):
    client.force_login(owner)
    r = client.post(reverse("campaign_create"), dict(valid_data, image=image_file(), creator=999, status="ACTIVA"), follow=True)
    c = Campaign.objects.get()
    assert c.creator == owner and c.status == "BORRADOR"
    assert c.image.storage.exists(c.image.name)
    assert "Campaña creada correctamente" in r.content.decode()

@pytest.mark.parametrize("field", ["title", "description", "category", "funding_goal", "deadline"])
def test_ca4_required(client, owner, valid_data, field):
    client.force_login(owner); valid_data[field] = ""
    r = client.post(reverse("campaign_create"), valid_data)
    assert field in r.context["form"].errors and not Campaign.objects.exists()

@pytest.mark.parametrize("field,value", [("funding_goal", "0"), ("funding_goal", "-1"), ("funding_goal", "NaN"), ("deadline", "2000-01-01"), ("title", "x"*121)])
def test_ca5_ca6_ca8_invalid_values(client, owner, valid_data, field, value):
    client.force_login(owner); valid_data[field] = value
    r = client.post(reverse("campaign_create"), valid_data)
    assert field in r.context["form"].errors and not Campaign.objects.exists()

@pytest.mark.parametrize("fmt,name,size,ok", [("JPEG", "photo.jpg", None, True), ("PNG", "photo.png", 2*1024*1024, True), ("PNG", "photo.png", 2*1024*1024+1, False), ("GIF", "photo.gif", None, False), ("PNG", "photo.txt", None, False)])
def test_ca7_image_format_and_size(client, owner, valid_data, image_file, fmt, name, size, ok):
    client.force_login(owner)
    r = client.post(reverse("campaign_create"), dict(valid_data, image=image_file(fmt, name, size)))
    assert Campaign.objects.exists() == ok
    if not ok: assert "image" in r.context["form"].errors

def test_ca7_corrupt_image_rejected(client, owner, valid_data):
    from django.core.files.uploadedfile import SimpleUploadedFile
    client.force_login(owner)
    r = client.post(reverse("campaign_create"), dict(valid_data, image=SimpleUploadedFile("bad.jpg", b"broken")))
    assert "image" in r.context["form"].errors and not Campaign.objects.exists()

def test_ca9_valid_values_retained(client, owner, valid_data):
    client.force_login(owner)
    r = client.post(reverse("campaign_create"), dict(valid_data, funding_goal="0"))
    for field in ["title", "description", "category", "deadline"]:
        assert str(r.context["form"][field].value()) == str(valid_data[field])
    assert valid_data["title"] in r.content.decode()

def test_publication_explicit_owner_post_only(client, owner, other, campaign_factory):
    c = campaign_factory(status="BORRADOR")
    url = reverse("campaign_publish", args=[c.pk])
    client.force_login(other)
    assert client.post(url).status_code == 404
    client.force_login(owner)
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 302
    c.refresh_from_db(); assert c.status == "ACTIVA"
    assert client.post(url).status_code == 403
