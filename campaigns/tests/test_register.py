import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_registro_valido_crea_usuario_y_redirige_a_login(client):
    """
    CA1:
    Un visitante ingresa un correo válido no registrado y dos
    contraseñas válidas coincidentes.

    Debe crear la cuenta y redirigir al Login.
    """
    response = client.post(
        reverse("register"),
        {
            "email": "usuario@ejemplo.com",
            "password1": "ClaveSegura123!",
            "password2": "ClaveSegura123!",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("login")

    assert User.objects.filter(
        email="usuario@ejemplo.com"
    ).exists()

    user = User.objects.get(email="usuario@ejemplo.com")

    assert user.username == "usuario@ejemplo.com"
    assert user.check_password("ClaveSegura123!")


@pytest.mark.django_db
def test_registro_rechaza_correo_duplicado(client):
    """
    CA2:
    Si el correo ya está registrado, no debe crearse una
    segunda cuenta y debe mostrarse un error.
    """
    User.objects.create_user(
        username="usuario@ejemplo.com",
        email="usuario@ejemplo.com",
        password="ClaveSegura123!",
    )

    response = client.post(
        reverse("register"),
        {
            "email": "usuario@ejemplo.com",
            "password1": "OtraClave123!",
            "password2": "OtraClave123!",
        },
    )

    assert response.status_code == 200

    assert User.objects.filter(
        email__iexact="usuario@ejemplo.com"
    ).count() == 1

    assert "Este correo ya está registrado." in response.content.decode()


@pytest.mark.django_db
def test_registro_rechaza_datos_invalidos(client):
    """
    CA3:
    Si los datos son inválidos, debe mostrar errores y
    no crear la cuenta.
    """
    response = client.post(
        reverse("register"),
        {
            "email": "correo-invalido",
            "password1": "ClaveSegura123!",
            "password2": "ContraseñaDistinta123!",
        },
    )

    assert response.status_code == 200
    assert User.objects.count() == 0

    # El formulario debe contener errores de validación.
    assert response.context["form"].errors


@pytest.mark.django_db
def test_usuario_autenticado_no_puede_acceder_al_registro(client):
    """
    CA4:
    Un usuario que ya inició sesión e intenta acceder
    al Registro debe ser redirigido al inicio.
    """
    user = User.objects.create_user(
        username="usuario@ejemplo.com",
        email="usuario@ejemplo.com",
        password="ClaveSegura123!",
    )

    client.force_login(user)

    response = client.get(reverse("register"))

    assert response.status_code == 302
    assert response.url == reverse("home")
