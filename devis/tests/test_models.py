"""Tests des modèles de devis et des calculs."""

import pytest
from decimal import Decimal

from devis.models import Quote, QuoteItem
from devis.services.calculations import line_total, quote_total


@pytest.mark.django_db
def test_quote_str_and_has_client():
    quote = Quote.objects.create(title="Mariage", client_name="Jean")
    assert "Mariage" in str(quote)
    assert "Jean" in str(quote)
    assert quote.has_client is True

    bare = Quote.objects.create(title="Bapteme")
    assert bare.has_client is False
    assert "Bapteme" in str(bare)


@pytest.mark.django_db
def test_quote_total_without_items_is_zero():
    quote = Quote.objects.create(title="Vide")
    assert quote.total == Decimal("0.00")


@pytest.mark.django_db
def test_quote_total_sums_items():
    quote = Quote.objects.create(title="Evenement")
    QuoteItem.objects.create(
        quote=quote, label="Salle", quantity=Decimal("2"), unit_price=Decimal("50000")
    )
    QuoteItem.objects.create(
        quote=quote, label="Traiteur", quantity=Decimal("1.5"), unit_price=Decimal("20100.10")
    )
    assert quote.total == Decimal("130150.15")


@pytest.mark.django_db
def test_line_total_rounds_to_two_decimals():
    quote = Quote.objects.create(title="Arrondi")
    item = QuoteItem.objects.create(
        quote=quote, label="Ligne", quantity=Decimal("1.5"), unit_price=Decimal("10.01")
    )
    assert line_total(item) == Decimal("15.02")  # 15.015 → 15.02 (HALF_UP)
    assert quote_total(quote) == Decimal("15.02")


@pytest.mark.django_db
def test_quote_item_defaults_and_str():
    quote = Quote.objects.create(title="Defauts")
    item = QuoteItem.objects.create(quote=quote, label="Decoration")
    assert item.quantity == Decimal("1.00")
    assert item.unit_price == Decimal("0.00")
    assert str(item) == "Decoration"


@pytest.mark.django_db
def test_deleting_quote_removes_items():
    quote = Quote.objects.create(title="ASupprimer")
    QuoteItem.objects.create(quote=quote, label="Ligne")
    quote_id = quote.pk
    quote.delete()
    assert not QuoteItem.objects.filter(quote_id=quote_id).exists()
