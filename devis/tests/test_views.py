"""Tests des vues de devis : liste, formulaire, transitions, PDF et lignes."""

from decimal import Decimal

import pytest

from devis.models import Quote, QuoteItem

BASE_DATA = {
    "title": "",
    "client_name": "Jean Mbarga",
    "client_phone": "+237 690 00 00 00",
    "client_email": "",
    "client_address": "",
    "event_location": "Douala",
    "event_date": "",
    "valid_until": "",
    "discount": "0",
    "transport_cost": "0",
    "deposit_amount": "0",
    "notes": "",
    "items-TOTAL_FORMS": "1",
    "items-INITIAL_FORMS": "0",
    "items-MIN_NUM_FORMS": "0",
    "items-MAX_NUM_FORMS": "1000",
    "items-0-title": "Location de chaises",
    "items-0-quantity": "100",
    "items-0-unit_price": "500",
}


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", password="Pass1234!", is_staff=True
    )


@pytest.fixture
def auth_client(client, staff):
    client.force_login(staff)
    return client


@pytest.fixture
def quote(db):
    return Quote.objects.create(
        client_name="Marie Nkolo",
        client_phone="+237 655 11 22 33",
        event_location="Yaoundé",
    )


def test_quote_list_requires_login(client):
    response = client.get("/devis/")
    assert response.status_code == 302
    assert "/connexion/" in response["Location"]


@pytest.mark.django_db
def test_quote_list_displays_reference_and_client(auth_client, quote):
    response = auth_client.get("/devis/")
    assert response.status_code == 200
    body = response.content.decode()
    assert quote.reference in body
    assert "Marie Nkolo" in body


@pytest.mark.django_db
def test_quote_list_searches_by_client(auth_client, quote):
    Quote.objects.create(
        client_name="Paul Essomba",
        client_phone="+237 677 00 00 00",
        event_location="Bafoussam",
    )
    response = auth_client.get("/devis/", {"q": "Essomba"})
    body = response.content.decode()
    assert "Paul Essomba" in body
    assert "Marie Nkolo" not in body


@pytest.mark.django_db
def test_quote_list_filters_by_status(auth_client, quote):
    quote.status = Quote.Status.SENT
    quote.save()
    response = auth_client.get("/devis/", {"status": "sent"})
    assert [q.pk for q in response.context["quotes"]] == [quote.pk]


@pytest.mark.django_db
def test_quote_create_with_items(auth_client):
    response = auth_client.post("/devis/nouveau/", BASE_DATA)
    quote = Quote.objects.get()
    assert response.status_code == 302
    assert response["Location"] == f"/devis/{quote.pk}/"
    assert quote.reference.startswith("DEV-")
    assert quote.subtotal == Decimal("50000.00")
    assert quote.total_amount == Decimal("50000.00")
    assert quote.items.count() == 1
    assert quote.items.get().total_price == Decimal("50000.00")


@pytest.mark.django_db
def test_quote_create_requires_client_name(auth_client):
    response = auth_client.post("/devis/nouveau/", {**BASE_DATA, "client_name": ""})
    assert response.status_code == 200
    assert "client_name" in response.context["form"].errors
    assert Quote.objects.count() == 0


@pytest.mark.django_db
def test_quote_create_requires_client_phone(auth_client):
    response = auth_client.post("/devis/nouveau/", {**BASE_DATA, "client_phone": ""})
    assert response.status_code == 200
    assert "client_phone" in response.context["form"].errors


@pytest.mark.django_db
def test_quote_create_requires_event_location(auth_client):
    response = auth_client.post("/devis/nouveau/", {**BASE_DATA, "event_location": ""})
    assert response.status_code == 200
    assert "event_location" in response.context["form"].errors


@pytest.mark.django_db
def test_quote_create_requires_at_least_one_line(auth_client):
    data = {
        **BASE_DATA,
        "items-0-title": "",
        "items-0-quantity": "1",
        "items-0-unit_price": "0",
    }
    response = auth_client.post("/devis/nouveau/", data)
    assert response.status_code == 200
    assert "Ajoutez au moins une ligne" in response.content.decode()
    assert Quote.objects.count() == 0


@pytest.mark.django_db
def test_quote_create_rejects_discount_above_subtotal(auth_client):
    data = {**BASE_DATA, "discount": "90000"}
    response = auth_client.post("/devis/nouveau/", data)
    assert response.status_code == 200
    assert "discount" in response.context["form"].errors
    assert Quote.objects.count() == 0


@pytest.mark.django_db
def test_quote_create_rejects_deposit_above_total(auth_client):
    data = {**BASE_DATA, "deposit_amount": "90000"}
    response = auth_client.post("/devis/nouveau/", data)
    assert response.status_code == 200
    assert "deposit_amount" in response.context["form"].errors


@pytest.mark.django_db
def test_quote_detail_shows_client_and_item(auth_client, quote):
    QuoteItem.objects.create(
        quote=quote, title="Traiteur", quantity=1, unit_price=Decimal("30000")
    )
    response = auth_client.get(f"/devis/{quote.pk}/")
    assert response.status_code == 200
    assert response.context["quote"] == quote
    assert response.context["balance"] == Decimal("30000.00")
    body = response.content.decode()
    assert "Marie Nkolo" in body
    assert "Yaoundé" in body


@pytest.mark.django_db
def test_quote_update_adds_and_removes_lines(auth_client, quote):
    kept = QuoteItem.objects.create(
        quote=quote, title="Salle", quantity=1, unit_price=Decimal("10000")
    )
    removed = QuoteItem.objects.create(
        quote=quote, title="Déco", quantity=1, unit_price=Decimal("5000")
    )
    data = {
        **BASE_DATA,
        "items-TOTAL_FORMS": "3",
        "items-INITIAL_FORMS": "2",
        "items-0-id": str(kept.pk),
        "items-0-title": "Salle",
        "items-0-quantity": "2",
        "items-0-unit_price": "10000",
        "items-1-id": str(removed.pk),
        "items-1-title": "Déco",
        "items-1-quantity": "1",
        "items-1-unit_price": "5000",
        "items-1-DELETE": "on",
        "items-2-title": "Gâteau",
        "items-2-quantity": "1",
        "items-2-unit_price": "15000",
    }
    response = auth_client.post(f"/devis/{quote.pk}/modifier/", data)
    assert response.status_code == 302
    quote.refresh_from_db()
    assert quote.items.count() == 2
    assert quote.total_amount == Decimal("35000.00")
    assert not QuoteItem.objects.filter(pk=removed.pk).exists()


@pytest.mark.django_db
def test_quote_update_locked_when_not_draft(auth_client, quote):
    quote.status = Quote.Status.SENT
    quote.save()
    response = auth_client.get(f"/devis/{quote.pk}/modifier/", follow=True)
    assert response.redirect_chain[-1][0] == f"/devis/{quote.pk}/"
    assert "ne peut plus être modifié" in response.content.decode()


@pytest.mark.django_db
def test_quote_status_transition(auth_client, quote):
    response = auth_client.post(f"/devis/{quote.pk}/statut/", {"status": "sent"})
    assert response.status_code == 302
    quote.refresh_from_db()
    assert quote.status == Quote.Status.SENT


@pytest.mark.django_db
def test_quote_invalid_status_transition_is_rejected(auth_client, quote):
    response = auth_client.post(
        f"/devis/{quote.pk}/statut/", {"status": "accepted"}, follow=True
    )
    quote.refresh_from_db()
    assert quote.status == Quote.Status.DRAFT
    assert "Transition impossible" in response.content.decode()


@pytest.mark.django_db
def test_quote_delete_only_draft(auth_client, quote):
    sent = Quote.objects.create(
        client_name="Paul",
        client_phone="+237 677 00 00 00",
        event_location="Kribi",
        status=Quote.Status.SENT,
    )
    blocked = auth_client.post(f"/devis/{sent.pk}/supprimer/")
    assert blocked.status_code == 302
    assert Quote.objects.filter(pk=sent.pk).exists()

    response = auth_client.post(f"/devis/{quote.pk}/supprimer/")
    assert response.status_code == 302
    assert response["Location"] == "/devis/"
    assert not Quote.objects.filter(pk=quote.pk).exists()


@pytest.mark.django_db
def test_quote_item_add_and_delete(auth_client, quote):
    response = auth_client.post(
        f"/devis/{quote.pk}/ligne/",
        {"title": "Serveurs", "quantity": "3", "unit_price": "10000"},
    )
    assert response.status_code == 302
    item = quote.items.get()
    quote.refresh_from_db()
    assert quote.total_amount == Decimal("30000.00")

    response = auth_client.post(f"/devis/ligne/{item.pk}/supprimer/")
    assert response.status_code == 302
    assert not QuoteItem.objects.filter(pk=item.pk).exists()
    quote.refresh_from_db()
    assert quote.total_amount == Decimal("0.00")


@pytest.mark.django_db
def test_quote_item_add_locked_when_not_draft(auth_client, quote):
    quote.status = Quote.Status.SENT
    quote.save()
    response = auth_client.post(
        f"/devis/{quote.pk}/ligne/",
        {"title": "Serveurs", "quantity": "1", "unit_price": "1000"},
    )
    assert response.status_code == 302
    assert quote.items.count() == 0


@pytest.mark.django_db
def test_quote_pdf_download(auth_client, quote):
    QuoteItem.objects.create(
        quote=quote, title="Traiteur", quantity=1, unit_price=Decimal("30000")
    )
    quote.refresh_from_db()
    response = auth_client.get(f"/devis/{quote.pk}/pdf/")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


@pytest.mark.django_db
def test_quote_list_filters_are_ajax_ready(auth_client, quote):
    """Une requête de filtre AJAX ne renvoie que le bloc de résultats."""
    full = auth_client.get("/devis/")
    assert "<html" in full.content.decode()

    partial = auth_client.get("/devis/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert partial.status_code == 200
    body = partial.content.decode()
    assert "<html" not in body
    assert quote.reference in body
