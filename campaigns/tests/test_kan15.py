from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from campaigns.models import Campaign, Comment

pytestmark = pytest.mark.django_db


def create_url(campaign):
    return reverse('comment_create', args=[campaign.pk])


def delete_url(comment, campaign=None):
    return reverse('comment_delete', args=[campaign.pk if campaign else comment.campaign_id, comment.pk])


@pytest.fixture
def comment(campaign_factory, other):
    return Comment.objects.create(campaign=campaign_factory(), author=other, content='Comentario inicial')


@pytest.mark.parametrize('as_owner', [False, True])
def test_cp01_publish_association(client, owner, other, campaign_factory, as_owner):
    campaign = campaign_factory()
    unrelated = campaign_factory()
    user = owner if as_owner else other
    client.force_login(user)
    response = client.post(create_url(campaign), {
        'content': '  Una buena idea  ', 'author': unrelated.creator_id,
        'campaign': unrelated.pk, 'created_at': '2000-01-01',
    }, follow=True)
    saved = Comment.objects.get()
    assert saved.author == user and saved.campaign == campaign
    assert saved.content == 'Una buena idea'
    assert saved.created_at.date() == timezone.now().date()
    assert response.redirect_chain == [(campaign.get_absolute_url() + '#comentarios', 302)]
    html = response.content.decode()
    assert user.username in html and saved.content in html
    assert timezone.localtime(saved.created_at).strftime('%d/%m/%Y %H:%M') in html


def test_cp02_public_order_isolation(client, comment, owner, campaign_factory):
    campaign = comment.campaign
    older = Comment.objects.create(campaign=campaign, author=owner, content='Antiguo')
    Comment.objects.filter(pk=older.pk).update(created_at=timezone.now()-timedelta(days=1))
    tied = Comment.objects.create(campaign=campaign, author=owner, content='<script>alert(1)</script>')
    Comment.objects.filter(pk=tied.pk).update(created_at=comment.created_at)
    hidden = Comment.objects.create(campaign=campaign_factory(), author=owner, content='Otra campaña')
    response = client.get(campaign.get_absolute_url())
    assert list(response.context['comments']) == [tied, comment, older]
    html = response.content.decode()
    assert escape(tied.content) in html and tied.content not in html
    assert hidden.content not in html and 'Eliminar comentario</button>' not in html


def test_cp03_delete_own(client, comment):
    status = 'FINANCIADA'
    Campaign.objects.filter(pk=comment.campaign_id).update(status=status)
    client.force_login(comment.author)
    response = client.post(delete_url(comment), follow=True)
    assert response.status_code == 200
    assert 'Comentario eliminado correctamente.' in response.content.decode()
    assert not Comment.objects.exists()


@pytest.mark.parametrize('content,valid', [
    ('', False), (' \t\n\u2003 ', False), ('a', True),
    ('a'*1000, True), ('a'*1001, False),
])
def test_cp04_content_boundaries(client, other, campaign_factory, content, valid):
    campaign = campaign_factory()
    client.force_login(other)
    response = client.post(create_url(campaign), {} if content is None else {'content': content})
    assert response.status_code == (302 if valid else 200)
    assert Comment.objects.count() == int(valid)
    if valid:
        assert Comment.objects.get().content == content
    else:
        assert 'content' in response.context['comment_form'].errors
        assert 'errorlist' in response.content.decode()


@pytest.mark.parametrize('status,days,as_owner,expected', [
    ('BORRADOR', 1, True, 403),
    ('FINANCIADA', 1, False, 403), ('NO_FINANCIADA', 1, False, 403),
    ('ACTIVA', -1, False, 403),
])
def test_cp05_campaign_status(client, owner, other, campaign_factory, status, days, as_owner, expected):
    campaign = campaign_factory(status=status, deadline=timezone.localdate()+timedelta(days=days))
    client.force_login(owner if as_owner else other)
    assert client.post(create_url(campaign), {'content': 'Hola'}).status_code == expected
    assert Comment.objects.count() == int(expected == 302)
    if days < 0:
        campaign.refresh_from_db()
        assert campaign.status == Campaign.Status.NO_FINANCIADA


def test_cp06_anonymous_write(client, comment):
    response = client.post(create_url(comment.campaign), {'content': 'Intruso'})
    assert response.status_code == 302 and response.url.startswith(reverse('login')+'?next=')
    response = client.post(delete_url(comment))
    assert response.status_code == 302 and response.url.startswith(reverse('login')+'?next=')
    assert Comment.objects.count() == 1


def test_cp07_identifier_permissions(client, comment, owner, campaign_factory):
    # Even the campaign creator cannot delete another author's comment.
    client.force_login(owner)
    assert client.post(delete_url(comment), {'author': owner.pk}).status_code == 404
    client.force_login(comment.author)
    assert client.post(delete_url(comment, campaign_factory())).status_code == 404
    assert Comment.objects.filter(pk=comment.pk).exists()


def test_cp08_missing_or_private(client, comment):
    client.force_login(comment.author)
    assert client.get(reverse('campaign_detail', args=[999999])).status_code == 404
    assert client.post(reverse('comment_create', args=[999999])).status_code == 404
    assert client.post(reverse('comment_delete', args=[comment.campaign_id, 999999])).status_code == 404
    Campaign.objects.filter(pk=comment.campaign_id).update(status='BORRADOR')
    assert client.get(comment.campaign.get_absolute_url()).status_code == 404
    assert client.post(create_url(comment.campaign), {'content': 'Hola'}).status_code == 404
    assert Comment.objects.count() == 1


def test_cp09_http_methods(client, comment):
    client.force_login(comment.author)
    response = client.get(create_url(comment.campaign))
    assert response.status_code == 405 and response.headers['Allow'] == 'POST'
    response = client.delete(delete_url(comment))
    assert response.status_code == 405 and response.headers['Allow'] == 'POST'
    assert Comment.objects.count() == 1


def test_cp10_csrf(comment):
    client = Client(enforce_csrf_checks=True)
    client.force_login(comment.author)
    client.get(comment.campaign.get_absolute_url())
    token = client.cookies['csrftoken'].value
    assert client.post(create_url(comment.campaign), {'content': 'Sin token'}).status_code == 403
    assert client.post(delete_url(comment), HTTP_X_CSRFTOKEN='invalid').status_code == 403
    assert Comment.objects.count() == 1
    assert client.post(create_url(comment.campaign), {'content': 'Con token'}, HTTP_X_CSRFTOKEN=token).status_code == 302
    assert client.post(delete_url(comment), HTTP_X_CSRFTOKEN=token).status_code == 302
    assert Comment.objects.get().content == 'Con token'


def test_cp11_cp13_ui_and_contribution_error(client, comment, owner):
    campaign = comment.campaign
    public = client.get(campaign.get_absolute_url()).content.decode()
    assert 'Inicia sesión para comentar' in public and 'name="content"' not in public
    assert 'Eliminar comentario</button>' not in public
    client.force_login(comment.author)
    response = client.post(reverse('campaign_contribute', args=[campaign.pk]), {'amount': '-1'})
    assert 'amount' in response.context['contribution_form'].errors
    html = response.content.decode()
    assert 'name="content"' in html and comment.content in html
    assert 'Eliminar comentario</button>' in html
    Campaign.objects.filter(pk=campaign.pk).update(status='FINANCIADA')
    closed = client.get(campaign.get_absolute_url()).content.decode()
    assert 'name="content"' not in closed and 'Esta campaña no acepta nuevos comentarios.' in closed
    client.force_login(owner)
    assert 'Eliminar comentario</button>' not in client.get(campaign.get_absolute_url()).content.decode()
    comment.delete()
    assert 'Aún no hay comentarios.' in client.get(campaign.get_absolute_url()).content.decode()


def test_cp12_xss_unicode_and_errors(client, comment):
    user = comment.author
    user.username = '<img src=x onerror=alert(1)>'
    user.save()
    client.force_login(user)
    content = '¡Ánimo! 中文 🌱 <script>alert(1)</script>'
    assert client.post(create_url(comment.campaign), {'content': content}).status_code == 302
    html = client.get(comment.campaign.get_absolute_url()).content.decode()
    assert escape(content) in html and content not in html
    assert Comment.objects.order_by('-pk').first().content == content
    payload = '</textarea><script>alert(1)</script>' + 'x'*1001
    response = client.post(create_url(comment.campaign), {'content': payload})
    html = response.content.decode()
    assert escape(payload) in html and payload not in html
    assert escape(user.username) in html and user.username not in html
    assert Comment.objects.count() == 2
