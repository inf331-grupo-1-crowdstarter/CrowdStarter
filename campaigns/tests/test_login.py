import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.fixture
def usuario(db):
    return User.objects.create_user(
        username="usuario@ejemplo.com",
        email="usuario@ejemplo.com",
        password="ClaveSegura123!",
    )


@pytest.mark.django_db
def test_login_correcto_inicia_sesion_y_redirige_inicio(client, usuario):
    """
    CA1:
    Credenciales correctas -> inicia sesión y redirige al inicio.
    """
    response = client.post(
        reverse("login"),
        {
            "username": "usuario@ejemplo.com",
            "password": "ClaveSegura123!",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("home")

    # Comprueba que realmente quedó autenticado.
    assert "_auth_user_id" in client.session
    assert int(client.session["_auth_user_id"]) == usuario.id


@pytest.mark.django_db
def test_login_incorrecto_muestra_mensaje_generico(client, usuario):
    """
    CA2:
    Credenciales incorrectas -> muestra un mensaje genérico
    sin revelar qué dato fue incorrecto.
    """
    response = client.post(
        reverse("login"),
        {
            "username": "usuario@ejemplo.com",
            "password": "ContraseñaIncorrecta123!",
        },
    )

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session

    contenido = response.content.decode()

    assert "Correo o contraseña incorrectos." in contenido


@pytest.mark.django_db
def test_logout_cierra_sesion_y_redirige_inicio(client, usuario):
    """
    CA3:
    Cerrar sesión -> termina la sesión y vuelve al inicio.
    """
    client.force_login(usuario)

    assert "_auth_user_id" in client.session

    response = client.get(reverse("logout"))

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_funcion_protegida_redirige_login_y_retorna_despues(client, usuario):
    """
    CA4:
    Usuario no autenticado intenta acceder a una función protegida
    -> Login -> después de autenticarse vuelve a la página solicitada.
    """
    protected_url = reverse("protected")

    response = client.get(protected_url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={protected_url}"

    response = client.post(
        reverse("login"),
        {
            "username": "usuario@ejemplo.com",
            "password": "ClaveSegura123!",
            "next": protected_url,
        },
    )

    assert response.status_code == 302
    assert response.url == protected_url

    response = client.get(protected_url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_usuario_autenticado_no_puede_acceder_login(client, usuario):
    """
    CA5:
    Usuario autenticado intenta acceder al Login
    -> es redirigido al inicio.
    """
    client.force_login(usuario)

    response = client.get(reverse("login"))

    assert response.status_code == 302
    assert response.url == reverse("home")
