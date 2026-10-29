import pytest
from django.urls import reverse
from campaigns.models import Category
pytestmark = pytest.mark.django_db

@pytest.mark.parametrize("query", ["SOLAR", "energÍA"])
def test_ca1_search_title_or_description_case_insensitive(client, campaign_factory, query):
    c = campaign_factory()
    campaign_factory(title="Otro", description="Sin coincidencia")
    assert list(client.get(reverse("campaign_list"), {"q": query}).context["page_obj"]) == [c]

@pytest.mark.parametrize("filters", ["category", "status", "combined"])
def test_ca2_ca3_ca4_filters_and_combination(client, campaign_factory, category, filters):
    c = campaign_factory()
    campaign_factory(category=Category.objects.create(name="Arte"), status="FINANCIADA", title="Otra", description="Otra")
    data = {"category": category.pk} if filters == "category" else {"status": "ACTIVA"}
    if filters == "combined": data.update(category=category.pk, q="solar")
    assert list(client.get(reverse("campaign_list"), data).context["page_obj"]) == [c]

def test_ca5_no_results(client):
    assert "No hay resultados" in client.get(reverse("campaign_list"), {"q": "nada"}).content.decode()

def test_ca6_ca7_retention_clear_and_pagination(client, campaign_factory, category):
    for _ in range(11): campaign_factory()
    data = {"q": "solar", "category": str(category.pk), "status": "ACTIVA"}
    r = client.get(reverse("campaign_list"), data)
    text = r.content.decode()
    assert 'value="solar"' in text
    assert f'value="{category.pk}" selected' in text
    assert 'value="ACTIVA" selected' in text
    assert 'q=solar&amp;category=' in text and 'status=ACTIVA&amp;page=2' in text
    assert f'href="{reverse("campaign_list")}">Limpiar filtros' in text
    assert len(client.get(reverse("campaign_list"), dict(data, page=2)).context["page_obj"]) == 1
    assert client.get(reverse("campaign_list")).context["query"] == ""
