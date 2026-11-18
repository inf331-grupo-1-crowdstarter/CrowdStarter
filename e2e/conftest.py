import os
from datetime import timedelta
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from campaigns.models import Campaign, Category


os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

E2E_PASSWORD = "E2ePassword123!"


@pytest.fixture
def e2e_user(db):
    return User.objects.create_user(
        username="e2e-user@example.com",
        email="e2e-user@example.com",
        password=E2E_PASSWORD,
    )


@pytest.fixture
def e2e_other_user(db):
    return User.objects.create_user(
        username="e2e-other@example.com",
        email="e2e-other@example.com",
        password=E2E_PASSWORD,
    )


@pytest.fixture
def e2e_category(db):
    return Category.objects.create(name="Tecnología e Innovación")


@pytest.fixture
def active_campaign(db, e2e_user, e2e_category):
    return Campaign.objects.create(
        title="Campaña E2E",
        description="Campaña creada para pruebas de interfaz",
        category=e2e_category,
        funding_goal="1000.00",
        deadline=timezone.localdate() + timedelta(days=30),
        creator=e2e_user,
        status=Campaign.Status.ACTIVA,
    )


@pytest.fixture
def draft_campaign(db, e2e_user, e2e_category):
    return Campaign.objects.create(
        title="Borrador privado E2E",
        description="No debe aparecer públicamente",
        category=e2e_category,
        funding_goal="1000.00",
        deadline=timezone.localdate() + timedelta(days=30),
        creator=e2e_user,
        status=Campaign.Status.BORRADOR,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    screenshots = Path("reports/screenshots")
    screenshots.mkdir(parents=True, exist_ok=True)
    filename = item.nodeid.replace("/", "_").replace(":", "_")
    page.screenshot(path=screenshots / f"{filename}.png", full_page=True)
