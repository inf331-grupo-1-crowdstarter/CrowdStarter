import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from campaigns.models import Campaign, Category


os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

E2E_PASSWORD = "E2ePassword123!"


def pytest_configure(config):
    base_url = os.environ.get("BASE_URL")
    if base_url is None:
        return

    message = (
        "BASE_URL debe ser http://localhost:PUERTO o http://127.0.0.1:PUERTO "
        "(1-65535), sin ruta, credenciales, consulta ni fragmento. "
        "PyTest inicia su propio servidor con una base de datos temporal."
    )
    try:
        url = urlsplit(base_url)
        port = url.port
    except ValueError as exc:
        raise pytest.UsageError(message) from exc
    if (
        url.scheme != "http"
        or url.hostname not in {"localhost", "127.0.0.1"}
        or not port
        or url.username is not None
        or url.password is not None
        or url.path not in {"", "/"}
        or "?" in base_url
        or "#" in base_url
        or base_url != base_url.strip()
    ):
        raise pytest.UsageError(message)

    address = f"{url.hostname}:{port}"
    for existing in (
        config.getoption("liveserver"),
        os.environ.get("DJANGO_LIVE_TEST_SERVER_ADDRESS"),
    ):
        if existing and existing != address:
            raise pytest.UsageError(
                "BASE_URL contradice --liveserver o DJANGO_LIVE_TEST_SERVER_ADDRESS. "
                "Utiliza una sola dirección para el servidor E2E."
            )
    config.option.liveserver = address


@pytest.fixture(scope="session")
def e2e_base_url(live_server):
    return live_server.url


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
