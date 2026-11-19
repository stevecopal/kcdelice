"""Validation des formulaires de devis."""

from decimal import Decimal

import pytest

from devis.forms import QuoteForm, QuoteItemForm

VALID_QUOTE = {
    "client_name": "Jean Mbarga",
    "client_phone": "+237 690 00 00 00",
    "event_location": "Douala",
}


@pytest.mark.django_db
def test_quote_form_accepts_full_client():
    form = QuoteForm(
        data={
            **VALID_QUOTE,
            "title": "Mariage",
            "client_email": "jean@example.com",
            "client_address": "Akwa",
            "event_date": "2026-12-24",
            "discount": "5000",
            "transport_cost": "1500",
            "deposit_amount": "20000",
        }
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["client_name"] == "Jean Mbarga"


@pytest.mark.django_db
def test_quote_form_requires_client_name():
    form = QuoteForm(data={**VALID_QUOTE, "client_name": ""})
    assert not form.is_valid()
    assert "client_name" in form.errors


@pytest.mark.django_db
def test_quote_form_requires_client_phone():
    form = QuoteForm(data={**VALID_QUOTE, "client_phone": ""})
    assert not form.is_valid()
    assert "client_phone" in form.errors


@pytest.mark.django_db
def test_quote_form_requires_event_location():
    form = QuoteForm(data={**VALID_QUOTE, "event_location": ""})
    assert not form.is_valid()
    assert "event_location" in form.errors


@pytest.mark.django_db
def test_quote_form_rejects_invalid_email():
    form = QuoteForm(data={**VALID_QUOTE, "client_email": "pas-un-email"})
    assert not form.is_valid()
    assert "client_email" in form.errors


@pytest.mark.django_db
def test_quote_form_rejects_negative_amounts():
    form = QuoteForm(
        data={**VALID_QUOTE, "discount": "-1", "transport_cost": "-1", "deposit_amount": "-1"}
    )
    assert not form.is_valid()
    for field in ("discount", "transport_cost", "deposit_amount"):
        assert field in form.errors


@pytest.mark.django_db
def test_quote_item_form_valid():
    form = QuoteItemForm(
        data={"title": "Salle", "quantity": "2", "unit_price": "15000.50"}
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["quantity"] == Decimal("2")
    assert form.cleaned_data["unit_price"] == Decimal("15000.50")


@pytest.mark.django_db
def test_quote_item_form_rejects_zero_quantity():
    form = QuoteItemForm(data={"title": "Salle", "quantity": "0", "unit_price": "10"})
    assert not form.is_valid()
    assert "quantity" in form.errors


@pytest.mark.django_db
def test_quote_item_form_rejects_negative_price():
    form = QuoteItemForm(data={"title": "Salle", "quantity": "1", "unit_price": "-5"})
    assert not form.is_valid()
    assert "unit_price" in form.errors


@pytest.mark.django_db
def test_quote_item_form_requires_title():
    form = QuoteItemForm(data={"quantity": "1", "unit_price": "10"})
    assert not form.is_valid()
    assert "title" in form.errors
