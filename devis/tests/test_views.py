"""Tests des vues de devis : accès privé, CRUD, pagination, messages."""

import uuid
from decimal import Decimal

import pytest
from django.urls import reverse

from devis.models import Quote, QuoteItem


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(username="admin", password="pass")


@pytest.fixture
def auth_client(client, admin_user):
    client.force_login(admin_user)
    return client


def test_quote_list_requires_login(client):
    response = client.get("/devis/")
    assert response.status_code == 302
    assert response["Location"].startswith("/admin/login/")
    assert "next=/devis/" in response["Location"]


@pytest.mark.django_db
def test_quote_list_displays_quotes(auth_client):
    Quote.objects.create(title="Devis Jean", client_name="Jean")
    Quote.objects.create(title="Devis Marie")
    response = auth_client.get("/devis/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Devis Jean" in content
    assert "Devis Marie" in content


@pytest.mark.django_db
def test_quote_list_paginates(auth_client):
    for index in range(11):
        Quote.objects.create(title=f"Devis {index:02d}")
    response = auth_client.get("/devis/")
    assert len(response.context["quotes"]) == 10
    response = auth_client.get("/devis/?page=2")
    assert response.status_code == 200
    assert len(response.context["quotes"]) == 1


@pytest.mark.django_db
def test_quote_create_with_optional_client(auth_client):
    response = auth_client.get("/devis/nouveau/")
    assert response.status_code == 200

    response = auth_client.post(
        "/devis/nouveau/",
        {
            "title": "Devis test",
            "client_name": "Jean",
            "client_phone": "+237 600",
            "client_email": "jean@example.com",
        },
        follow=True,
    )
    assert response.redirect_chain
    quote = Quote.objects.get(title="Devis test")
    assert quote.client_name == "Jean"
    assert "Devis créé avec succès." in response.content.decode()


@pytest.mark.django_db
def test_quote_create_without_client_is_allowed(auth_client):
    response = auth_client.post(
        "/devis/nouveau/",
        {"title": "Devis sans client"},
    )
    assert response.status_code == 302
    quote = Quote.objects.get(title="Devis sans client")
    assert quote.has_client is False
    assert response["Location"] == reverse("quote_detail", args=[quote.pk])


@pytest.mark.django_db
def test_quote_create_invalid_form_renders_errors(auth_client):
    response = auth_client.post("/devis/nouveau/", {})
    assert response.status_code == 200
    assert Quote.objects.count() == 0
    assert "Ce champ est obligatoire." in response.content.decode()


@pytest.mark.django_db
def test_quote_detail_shows_items_and_total(auth_client):
    quote = Quote.objects.create(title="Devis complet", client_name="Jean")
    QuoteItem.objects.create(
        quote=quote, label="Salle", quantity=Decimal("1"), unit_price=Decimal("100000")
    )
    QuoteItem.objects.create(
        quote=quote, label="Traiteur", quantity=Decimal("2"), unit_price=Decimal("25000")
    )
    response = auth_client.get(reverse("quote_detail", args=[quote.pk]))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Salle" in content
    assert "Traiteur" in content
    assert "150000.00 FCFA" in content
    assert "Jean" in content


@pytest.mark.django_db
def test_quote_detail_unknown_pk_returns_404(auth_client):
    response = auth_client.get(reverse("quote_detail", args=[uuid.uuid4()]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_quote_detail_requires_login(client):
    quote = Quote.objects.create(title="Prive")
    response = client.get(reverse("quote_detail", args=[quote.pk]))
    assert response.status_code == 302


@pytest.mark.django_db
def test_quote_item_add_and_delete(auth_client):
    quote = Quote.objects.create(title="Devis lignes")
    response = auth_client.post(
        reverse("quote_item_add", args=[quote.pk]),
        {"label": "Decoration", "quantity": "1", "unit_price": "15000"},
        follow=True,
    )
    item = QuoteItem.objects.get(quote=quote, label="Decoration")
    assert item.unit_price == Decimal("15000")
    assert "Ligne ajoutée au devis." in response.content.decode()

    response = auth_client.post(
        reverse("quote_item_delete", args=[item.pk]), follow=True
    )
    assert not QuoteItem.objects.filter(pk=item.pk).exists()
    assert "Ligne supprimée." in response.content.decode()


@pytest.mark.django_db
def test_quote_item_add_unknown_quote_returns_404(auth_client):
    response = auth_client.post(
        reverse("quote_item_add", args=[uuid.uuid4()]),
        {"label": "X", "quantity": "1", "unit_price": "1"},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_quote_item_add_invalid_form_renders_errors(auth_client):
    quote = Quote.objects.create(title="Devis")
    response = auth_client.post(
        reverse("quote_item_add", args=[quote.pk]),
        {"label": "", "quantity": "0", "unit_price": "-1"},
    )
    assert response.status_code == 200
    assert QuoteItem.objects.count() == 0
    assert "Ce champ est obligatoire." in response.content.decode()
