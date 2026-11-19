"""Validation des formulaires de devis."""

from decimal import Decimal

from devis.forms import QuoteForm, QuoteItemForm


def test_quote_form_minimal_is_valid():
    form = QuoteForm(data={"title": "Devis anniversaire"})
    assert form.is_valid(), form.errors
    assert form.cleaned_data["client_name"] == ""
    assert form.cleaned_data["client_email"] == ""


def test_quote_form_requires_title():
    form = QuoteForm(data={})
    assert not form.is_valid()
    assert "title" in form.errors


def test_quote_form_rejects_invalid_email():
    form = QuoteForm(data={"title": "Devis", "client_email": "pas-un-email"})
    assert not form.is_valid()
    assert "client_email" in form.errors


def test_quote_form_accepts_full_client():
    form = QuoteForm(
        data={
            "title": "Devis complet",
            "client_name": "Jean",
            "client_phone": "+237 600",
            "client_email": "jean@example.com",
        }
    )
    assert form.is_valid(), form.errors


def test_quote_item_form_valid():
    form = QuoteItemForm(
        data={"label": "Salle", "quantity": "2", "unit_price": "15000.50"}
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["quantity"] == Decimal("2")
    assert form.cleaned_data["unit_price"] == Decimal("15000.50")


def test_quote_item_form_rejects_zero_quantity():
    form = QuoteItemForm(data={"label": "Salle", "quantity": "0", "unit_price": "10"})
    assert not form.is_valid()
    assert "quantity" in form.errors


def test_quote_item_form_rejects_negative_price():
    form = QuoteItemForm(
        data={"label": "Salle", "quantity": "1", "unit_price": "-5"}
    )
    assert not form.is_valid()
    assert "unit_price" in form.errors


def test_quote_item_form_requires_label():
    form = QuoteItemForm(data={"quantity": "1", "unit_price": "10"})
    assert not form.is_valid()
    assert "label" in form.errors
