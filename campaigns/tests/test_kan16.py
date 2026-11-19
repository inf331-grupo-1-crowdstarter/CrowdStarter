from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from campaigns.models import Campaign, CampaignUpdate

pytestmark = pytest.mark.django_db


def action_url(action, campaign, update=None):
    args = [campaign.pk]
    if update is not None:
        args.append(update.pk)
    return reverse('update_' + action, args=args)


@pytest.fixture
def update(campaign_factory, owner):
    return CampaignUpdate.objects.create(
        campaign=campaign_factory(), author=owner, title='Primer avance', content='Contenido inicial')


@pytest.mark.parametrize('status', ['ACTIVA', 'FINANCIADA'])
def test_k16_01_create_and_association(client, owner, other, campaign_factory, status):
    """Publicar en estados permitidos persiste autor y campaña reales, ignorando IDs manipulados."""
    campaign = campaign_factory(status=status)
    unrelated = campaign_factory(creator=other)
    client.force_login(owner)
    response = client.post(action_url('create', campaign), {
        'title': '  Avance 🌱  ', 'content': '  ¡Éxito! 中文\nSegundo párrafo  ',
        'author': other.pk, 'campaign': unrelated.pk, 'created_at': '2000-01-01',
    }, follow=True)
    saved = CampaignUpdate.objects.get()
    assert saved.campaign == campaign and saved.author == owner
    assert saved.title == 'Avance 🌱' and saved.content == '¡Éxito! 中文\nSegundo párrafo'
    assert response.redirect_chain == [(campaign.get_absolute_url() + '#actualizaciones', 302)]
    html = response.content.decode()
    assert 'Actualización publicada correctamente.' in html and saved.title in html
    assert owner.username in html
    assert timezone.localtime(saved.created_at).strftime('%d/%m/%Y %H:%M') in html


def test_k16_02_edit_own(client, owner, other, update, campaign_factory):
    """Editar una actualización propia conserva identidad y fecha de publicación tras pasar a NO_FINANCIADA."""
    campaign = update.campaign
    Campaign.objects.filter(pk=campaign.pk).update(status='NO_FINANCIADA')
    client.force_login(owner)
    response = client.get(action_url('edit', campaign, update))
    assert response.context['form'].initial['title'] == update.title
    created_at = update.created_at
    response = client.post(action_url('edit', campaign, update), {
        'title': 'Avance corregido', 'content': 'Contenido editado',
        'author': other.pk, 'campaign': campaign_factory().pk,
    }, follow=True)
    assert 'Actualización editada correctamente.' in response.content.decode()
    update.refresh_from_db()
    assert update.title == 'Avance corregido' and update.content == 'Contenido editado'
    assert update.campaign == campaign and update.author == owner
    assert update.created_at == created_at and update.updated_at >= created_at
    assert CampaignUpdate.objects.count() == 1


def test_k16_03_delete_own(client, owner, update):
    """Eliminar una actualización propia funciona en FINANCIADA y conserva la campaña."""
    Campaign.objects.filter(pk=update.campaign_id).update(status='FINANCIADA')
    client.force_login(owner)
    response = client.post(action_url('delete', update.campaign, update), follow=True)
    assert 'Actualización eliminada correctamente.' in response.content.decode()
    assert not CampaignUpdate.objects.exists()
    assert Campaign.objects.filter(pk=update.campaign_id).exists()


def test_k16_04_public_order_and_isolation(client, owner, update, campaign_factory):
    """Visitantes leen solo actualizaciones de su campaña, con orden descendente y desempate por ID."""
    older = CampaignUpdate.objects.create(campaign=update.campaign, author=owner, title='Antigua', content='Anterior')
    CampaignUpdate.objects.filter(pk=older.pk).update(created_at=timezone.now()-timedelta(days=1))
    tied = CampaignUpdate.objects.create(campaign=update.campaign, author=owner, title='Empatada', content='Reciente')
    CampaignUpdate.objects.filter(pk=tied.pk).update(created_at=update.created_at)
    hidden = CampaignUpdate.objects.create(campaign=campaign_factory(), author=owner, title='Otra campaña', content='Oculta')
    html = client.get(update.campaign.get_absolute_url()).content.decode()
    assert html.index('Empatada') < html.index(update.title) < html.index('Antigua')
    assert hidden.title not in html
    assert 'Editar actualización' not in html and 'Eliminar actualización' not in html
    assert 'Publicar actualización' not in html


@pytest.mark.parametrize('status,days,expected', [
    ('BORRADOR', 10, 403), ('NO_FINANCIADA', 10, 403),
    ('ACTIVA', -1, 403),
], ids=['borrador', 'no-financiada', 'activa-vencida'])
def test_k16_05_publication_status(client, owner, campaign_factory, status, days, expected):
    """Estados prohibidos y activa vencida rechazan publicación; financiada puede publicar tras su fecha límite."""
    campaign = campaign_factory(status=status, deadline=timezone.localdate()+timedelta(days=days))
    client.force_login(owner)
    response = client.post(action_url('create', campaign), {'title': 'Avance', 'content': 'Contenido'})
    assert response.status_code == expected
    assert CampaignUpdate.objects.count() == int(expected == 302)
    html = client.get(campaign.get_absolute_url()).content.decode()
    assert ('Publicar actualización' in html) == (expected == 302)
    if status == 'ACTIVA' and days < 0:
        campaign.refresh_from_db()
        assert campaign.status == Campaign.Status.NO_FINANCIADA


@pytest.mark.parametrize('field,value,valid', [
    ('title', '', False), ('title', ' \t\n\u2003 ', False),
    ('title', 'a', True), ('title', 'a'*150, True), ('title', 'a'*151, False),
    ('content', '', False), ('content', ' \t\n\u2003 ', False),
    ('content', 'a', True), ('content', 'a'*5000, True), ('content', 'a'*5001, False),
], ids=['titulo-vacio', 'titulo-espacios', 'titulo-1', 'titulo-150', 'titulo-151',
        'contenido-vacio', 'contenido-espacios', 'contenido-1', 'contenido-5000', 'contenido-5001'])
def test_k16_06_validation(client, owner, update, field, value, valid):
    """Límites y campos vacíos se validan al publicar, sin persistir entradas inválidas."""
    action = 'create'
    client.force_login(owner)
    data = {'title': 'Título válido', 'content': 'Contenido válido', field: value}
    url = action_url(action, update.campaign, update if action == 'edit' else None)
    response = client.post(url, data)
    assert response.status_code == (302 if valid else 200)
    if valid:
        saved = CampaignUpdate.objects.order_by('-pk').first()
        assert getattr(saved, field) == value
    else:
        assert field in response.context['form'].errors
        assert 'errorlist' in response.content.decode()
        update.refresh_from_db()
        assert update.title == 'Primer avance' and update.content == 'Contenido inicial'
    assert CampaignUpdate.objects.count() == (2 if valid and action == 'create' else 1)


def test_k16_07_authentication(client, update):
    """Las tres escrituras sin sesión redirigen a login y dejan los datos intactos."""
    create = client.post(action_url('create', update.campaign), {'title': 'Intruso', 'content': 'Intruso'})
    edit = client.post(action_url('edit', update.campaign, update), {'title': 'Intruso', 'content': 'Intruso'})
    delete = client.post(action_url('delete', update.campaign, update))
    assert all(r.status_code == 302 and r.url.startswith(reverse('login')+'?next=') for r in [create, edit, delete])
    update.refresh_from_db()
    assert update.title == 'Primer avance' and CampaignUpdate.objects.count() == 1


def test_k16_08_server_permissions(client, other, update):
    """Un usuario ajeno con privilegios de administrador no puede realizar ninguna escritura."""
    other.is_staff = True
    other.is_superuser = True
    other.save()
    client.force_login(other)
    data = {'title': 'Intruso', 'content': 'Intruso', 'author': other.pk}
    assert client.post(action_url('create', update.campaign), data).status_code == 404
    assert client.post(action_url('edit', update.campaign, update), data).status_code == 404
    assert client.post(action_url('delete', update.campaign, update)).status_code == 404
    update.refresh_from_db()
    assert update.title == 'Primer avance' and CampaignUpdate.objects.count() == 1


def test_k16_09_invalid_identifiers(client, owner, update, campaign_factory):
    """IDs inexistentes y mezcla de campaña/actualización devuelven 404 sin alterar datos."""
    client.force_login(owner)
    other_campaign = campaign_factory()
    data = {'title': 'Cambio', 'content': 'Cambio'}
    assert client.post(action_url('edit', other_campaign, update), data).status_code == 404
    assert client.post(action_url('delete', other_campaign, update)).status_code == 404
    assert client.post(reverse('update_create', args=[999999]), data).status_code == 404
    assert client.post(reverse('update_edit', args=[update.campaign_id, 999999]), data).status_code == 404
    assert client.post(reverse('update_delete', args=[update.campaign_id, 999999])).status_code == 404
    update.refresh_from_db()
    assert update.title == 'Primer avance' and CampaignUpdate.objects.count() == 1


def test_k16_11_csrf(update):
    """CSRF bloquea crear/editar/eliminar sin token válido y permite el ciclo completo con token válido."""
    client = Client(enforce_csrf_checks=True)
    client.force_login(update.author)
    client.get(update.campaign.get_absolute_url())
    token = client.cookies['csrftoken'].value
    data = {'title': 'Con CSRF', 'content': 'Contenido'}
    assert client.post(action_url('create', update.campaign), data).status_code == 403
    assert client.post(action_url('edit', update.campaign, update), data).status_code == 403
    assert client.post(action_url('delete', update.campaign, update), HTTP_X_CSRFTOKEN='incorrecto').status_code == 403
    assert CampaignUpdate.objects.count() == 1
    assert client.post(action_url('create', update.campaign), data, HTTP_X_CSRFTOKEN=token).status_code == 302
    created = CampaignUpdate.objects.order_by('-pk').first()
    assert client.post(action_url('edit', update.campaign, created), {'title': 'Editado', 'content': 'Contenido'}, HTTP_X_CSRFTOKEN=token).status_code == 302
    created.refresh_from_db()
    assert created.title == 'Editado'
    assert client.post(action_url('delete', update.campaign, created), HTTP_X_CSRFTOKEN=token).status_code == 302
    assert list(CampaignUpdate.objects.all()) == [update]


def test_k16_12_http_methods(client, owner, update):
    """PUT en crear, PATCH en editar y GET en eliminar no mutan datos y devuelven Allow correcto."""
    client.force_login(owner)
    create = client.put(action_url('create', update.campaign))
    edit = client.patch(action_url('edit', update.campaign, update))
    delete = client.get(action_url('delete', update.campaign, update))
    assert create.status_code == edit.status_code == delete.status_code == 405
    assert create.headers['Allow'] == edit.headers['Allow'] == 'GET, POST'
    assert delete.headers['Allow'] == 'POST'
    assert CampaignUpdate.objects.count() == 1


def test_k16_13_xss(client, owner, update):
    """Título, contenido, autor y valores de formulario rechazados se escapan sin ejecutar etiquetas."""
    owner.username = '<img src=x onerror=alert(1)>'
    owner.save()
    client.force_login(owner)
    title = '<script>alert(1)</script>'
    content = '<img src=x onerror=alert(2)>\n¡Avance! 中文 🌱'
    assert client.post(action_url('edit', update.campaign, update), {'title': title, 'content': content}).status_code == 302
    client.logout()
    html = client.get(update.campaign.get_absolute_url()).content.decode()
    assert title not in html and escape(title) in html
    assert '<img src=x onerror=alert(2)>' not in html and escape('<img src=x onerror=alert(2)>') in html
    assert owner.username not in html and escape(owner.username) in html
    assert '中文 🌱' in html
    client.force_login(owner)
    payload = '</textarea><script>alert(3)</script>' + 'x'*5001
    response = client.post(action_url('edit', update.campaign, update), {'title': title, 'content': payload})
    assert escape(payload) in response.content.decode() and payload not in response.content.decode()
    update.refresh_from_db()
    assert update.content == content


def test_k16_14_detail_integration(client, owner, other, campaign_factory):
    """Detalle vacío/público, controles del creador, error de aporte y privacidad del borrador se integran correctamente."""
    campaign = campaign_factory()
    html = client.get(campaign.get_absolute_url()).content.decode()
    assert 'Aún no hay actualizaciones' in html and 'Publicar actualización' not in html
    client.force_login(owner)
    assert 'Publicar actualización' in client.get(campaign.get_absolute_url()).content.decode()
    assert client.get(action_url('create', campaign)).status_code == 200
    update = CampaignUpdate.objects.create(campaign=campaign, author=owner, title='Avance público', content='Contenido visible')
    own_html = client.get(campaign.get_absolute_url()).content.decode()
    assert 'Editar actualización' in own_html and 'Eliminar actualización' in own_html
    client.force_login(other)
    assert client.get(action_url('create', campaign)).status_code == 404
    response = client.post(reverse('campaign_contribute', args=[campaign.pk]), {'amount': '-1'})
    assert 'amount' in response.context['contribution_form'].errors
    html = response.content.decode()
    assert update.title in html and update.content in html
    assert 'Editar actualización' not in html and 'Eliminar actualización' not in html
    Campaign.objects.filter(pk=campaign.pk).update(status='BORRADOR')
    client.logout()
    assert client.get(campaign.get_absolute_url()).status_code == 404
