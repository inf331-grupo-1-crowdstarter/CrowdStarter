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
