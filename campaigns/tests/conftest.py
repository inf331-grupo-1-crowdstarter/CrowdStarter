from datetime import timedelta
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from campaigns.models import Category, Campaign

@pytest.fixture
def owner(db):
    return User.objects.create_user(username="owner@example.com", password="ClaveSegura123!")

@pytest.fixture
def other(db):
    return User.objects.create_user(username="other@example.com", password="ClaveSegura123!")

@pytest.fixture
def category(db):
    return Category.objects.create(name="Tecnología")

@pytest.fixture
def campaign_factory(owner, category):
    def make(**kwargs):
        data = dict(title="Proyecto solar", description="Energía para todos", category=category,
                    funding_goal="1000.00", deadline=timezone.localdate()+timedelta(days=30),
                    creator=owner, status=Campaign.Status.ACTIVA)
        data.update(kwargs)
        return Campaign.objects.create(**data)
    return make

@pytest.fixture
def valid_data(category):
    return dict(title="Nueva campaña", description="Una descripción", category=category.pk,
                funding_goal="1500.00", deadline=str(timezone.localdate()+timedelta(days=10)))

@pytest.fixture
def image_file():
    def make(fmt="PNG", name="image.png", size=None):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        data = BytesIO()
        Image.new("RGB", (10, 10), "blue").save(data, format=fmt)
        content = data.getvalue()
        if size: content += b" " * max(0, size-len(content))
        return SimpleUploadedFile(name, content, content_type="image/"+fmt.lower())
    return make

@pytest.fixture(autouse=True)
def isolated_media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"
