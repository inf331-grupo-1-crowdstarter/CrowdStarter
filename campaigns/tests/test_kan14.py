from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from campaigns.models import Contribution

pytestmark = pytest.mark.django_db
HISTORY = reverse("user_history_contributions")


def contribute(campaign, user, amount, days_ago):
    contribution = Contribution.objects.create(campaign=campaign, user=user, amount=amount)
    created_at = timezone.now() - timedelta(days=days_ago)
    Contribution.objects.filter(pk=contribution.pk).update(created_at=created_at)
    return created_at


def test_ca1_own_contributions_with_data_newest_first(client, campaign_factory, owner, other):
    solar = campaign_factory(title="Proyecto solar")
    huerto = campaign_factory(title="Huerto urbano")
    ajena = campaign_factory(title="Campaña de otro financiador")
    old_date = contribute(solar, other, 100, days_ago=5)
    new_date = contribute(huerto, other, 250, days_ago=1)
    contribute(ajena, owner, 999, days_ago=2)

    client.force_login(other)
    response = client.get(HISTORY)
    text = response.content.decode()

    assert response.status_code == 200
    for value in [solar.title, huerto.title, "100.00", "250.00",
                  timezone.localtime(old_date).strftime("%d/%m/%Y"),
                  timezone.localtime(new_date).strftime("%d/%m/%Y")]:
        assert value in text
    assert ajena.title not in text and "999.00" not in text
    assert text.index(huerto.title) < text.index(solar.title)


def test_ca2_no_contributions_message(client, other):
    client.force_login(other)
    text = client.get(HISTORY).content.decode()

    assert "Aún no has realizado aportes" in text


def test_ca2_message_hidden_when_has_contributions(client, campaign_factory, other):
    contribute(campaign_factory(), other, 100, days_ago=1)
    client.force_login(other)
    text = client.get(HISTORY).content.decode()

    assert "Aún no has realizado aportes" not in text


def test_ca3_campaign_links_to_detail(client, campaign_factory, other):
    c = campaign_factory()
    contribute(c, other, 100, days_ago=1)
    client.force_login(other)
    text = client.get(HISTORY).content.decode()

    assert f'href="{c.get_absolute_url()}"' in text
    assert client.get(c.get_absolute_url()).status_code == 200


def test_anonymous_redirected_to_login(client):
    response = client.get(HISTORY)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_navbar_my_contributions_link(client, other):
    home = reverse("home")
    assert HISTORY not in client.get(home).content.decode()

    client.force_login(other)
    text = client.get(home).content.decode()
    assert "Mis aportes" in text and HISTORY in text
