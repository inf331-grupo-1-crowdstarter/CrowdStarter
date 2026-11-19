import re

import pytest
from playwright.sync_api import Page, expect

from e2e.conftest import E2E_PASSWORD


def login(page: Page, e2e_base_url, email: str, password: str):
    page.goto(f"{e2e_base_url}/login/")
    page.get_by_label("Correo electrónico").fill(email)
    page.get_by_label("Contraseña").fill(password)
    page.get_by_role("button", name="Iniciar sesión").click()


@pytest.mark.django_db(transaction=True)
def test_e2e01_register_and_login(page, e2e_base_url):
    page.goto(f"{e2e_base_url}/registro/")
    page.get_by_label("Correo electrónico").fill("new-user@example.com")
    page.locator("#id_password1").fill("NewPassword123!")
    page.locator("#id_password2").fill("NewPassword123!")
    page.get_by_role("button", name="Crear cuenta").click()

    expect(page).to_have_url(re.compile(r".*/login/"))
    expect(page.get_by_text("Cuenta creada correctamente")).to_be_visible()

    page.get_by_label("Correo electrónico").fill("new-user@example.com")
    page.get_by_label("Contraseña").fill("NewPassword123!")
    page.get_by_role("button", name="Iniciar sesión").click()

    expect(page).to_have_url(f"{e2e_base_url}/")
    expect(page.get_by_text("Cerrar sesión")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e02_invalid_login(page, e2e_base_url):
    page.goto(f"{e2e_base_url}/login/")
    page.get_by_label("Correo electrónico").fill("no-existe@example.com")
    page.get_by_label("Contraseña").fill("ClaveIncorrecta123!")
    page.get_by_role("button", name="Iniciar sesión").click()
    expect(page.get_by_text("Correo o contraseña incorrectos.")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e03_create_and_publish_campaign(page, e2e_base_url, e2e_user, e2e_category):
    login(page, e2e_base_url, e2e_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/crear/")
    page.get_by_label("Título").fill("Campaña creada por E2E")
    page.get_by_label("Descripción").fill("Descripción creada para una prueba de interfaz.")
    page.locator("#id_category").select_option(label=e2e_category.name)
    page.get_by_label("Meta").fill("1500")
    page.get_by_label("Fecha límite").fill("2099-12-31")
    page.get_by_role("button", name="Guardar campaña").click()

    expect(page.get_by_text("Campaña creada correctamente como borrador.")).to_be_visible()
    expect(page.get_by_text("Borrador", exact=True)).to_be_visible()
    
    page.get_by_role("button", name="Publicar campaña").click()

    expect(page.get_by_text("Campaña publicada.")).to_be_visible()
    expect(page.get_by_text("Activa")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e04_draft_is_not_public(page, e2e_base_url, draft_campaign):
    page.goto(f"{e2e_base_url}/campanas/")
    expect(page.get_by_text(draft_campaign.title)).not_to_be_visible()
    response = page.goto(f"{e2e_base_url}/campanas/{draft_campaign.pk}/")
    assert response.status == 404


@pytest.mark.django_db(transaction=True)
def test_e2e05_search_and_filter(page, e2e_base_url, active_campaign):
    page.goto(f"{e2e_base_url}/campanas/")
    page.get_by_label("Buscar por palabra").fill("Campaña E2E")
    page.get_by_role("button", name="Filtrar").click()
    expect(page.get_by_text(active_campaign.title)).to_be_visible()

    page.get_by_label("Buscar por palabra").fill("sin coincidencias")
    page.get_by_role("button", name="Filtrar").click()
    expect(page.get_by_text("No se encontraron campañas con esos criterios")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e06_valid_contribution_and_history(page, e2e_base_url, active_campaign, e2e_other_user):
    login(page, e2e_base_url, e2e_other_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/")
    page.get_by_label("Monto del aporte simulado").fill("100")
    page.get_by_role("button", name="Aportar").click()

    expect(page.get_by_text("Aporte simulado registrado correctamente")).to_be_visible()
    page.goto(f"{e2e_base_url}/mis-aportes/")
    expect(page.get_by_text(active_campaign.title)).to_be_visible()
    expect(page.get_by_text("Monto: $100.00")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e07_contribution_completes_campaign(page, e2e_base_url, active_campaign, e2e_other_user):
    login(page, e2e_base_url, e2e_other_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/")
    page.get_by_label("Monto del aporte simulado").fill("1000")
    page.get_by_role("button", name="Aportar").click()

    expect(page.get_by_text("Financiada")).to_be_visible()
    expect(page.get_by_role("button", name="Aportar")).not_to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e08_owner_cannot_contribute(page, e2e_base_url, active_campaign, e2e_user):
    login(page, e2e_base_url, e2e_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/")
    expect(page.get_by_role("button", name="Aportar")).not_to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e09_edit_and_delete_campaign(page, e2e_base_url, active_campaign, e2e_user):
    login(page, e2e_base_url, e2e_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/editar/")
    page.get_by_label("Título").fill("Título editado por E2E")
    page.get_by_role("button", name="Guardar campaña").click()
    expect(page.get_by_role("heading", name="Título editado por E2E")).to_be_visible()

    page.get_by_role("link", name="Eliminar").click()
    page.get_by_role("button", name="Confirmar eliminación").click()
    expect(page).to_have_url(re.compile(r".*/campanas/"))
    expect(page.get_by_text("Título editado por E2E")).not_to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e10_creator_panel_shows_owned_campaigns(
    page,
    e2e_base_url,
    active_campaign,
    draft_campaign,
    e2e_user,
):
    login(page, e2e_base_url, e2e_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/panel_del_creador/")
    expect(page.get_by_text(active_campaign.title)).to_be_visible()
    expect(page.get_by_text(draft_campaign.title)).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e11_create_and_delete_comment(page, e2e_base_url, active_campaign, e2e_other_user):
    login(page, e2e_base_url, e2e_other_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/")
    page.get_by_label("Tu comentario").fill("Comentario creado por E2E")
    page.get_by_role("button", name="Publicar comentario").click()
    expect(page.get_by_text("Comentario creado por E2E")).to_be_visible()

    page.get_by_role("button", name=re.compile("Eliminar mi comentario")).click()
    expect(page.get_by_text("Comentario creado por E2E")).not_to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_e2e12_create_edit_and_delete_update(page, e2e_base_url, active_campaign, e2e_user):
    login(page, e2e_base_url, e2e_user.email, E2E_PASSWORD)
    page.goto(f"{e2e_base_url}/campanas/{active_campaign.pk}/")

    page.get_by_role("link", name="Publicar actualización").click()
    page.get_by_label("Título").fill("Actualización E2E")
    page.get_by_label("Contenido").fill("Contenido publicado desde la prueba E2E.")
    page.get_by_role("button", name="Guardar actualización").click()
    expect(page.get_by_text("Actualización E2E")).to_be_visible()

    page.get_by_role("link", name="Editar actualización").click()
    page.get_by_label("Título").fill("Actualización editada E2E")
    page.get_by_role("button", name="Guardar actualización").click()
    expect(page.get_by_text("Actualización editada E2E")).to_be_visible()

    page.get_by_role("button", name="Eliminar actualización").click()
    expect(page.get_by_text("Actualización editada E2E")).not_to_be_visible()
