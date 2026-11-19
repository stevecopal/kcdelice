"""Tests des modèles de devis : référencement, calculs et cycle de vie."""

from decimal import Decimal

import pytest

from devis.models import Quote, QuoteItem
from devis.services.calculations import line_total, quote_total


def make_quote(**overrides):
    data = {
        "client_name": "Jean Mbarga",
        "client_phone": "+237 690 00 00 00",
        "event_location": "Douala",
    }
    data.update(overrides)
    return Quote.objects.create(**data)


@pytest.mark.django_db
def test_reference_is_generated_and_unique():
    first = make_quote()
    second = make_quote()
    assert first.reference.startswith("DEV-")
    assert first.reference != second.reference
    assert first.reference.endswith("0001")
    assert second.reference.endswith("0002")


@pytest.mark.django_db
def test_str_contains_reference_and_client():
    quote = make_quote()
    assert quote.reference in str(quote)
    assert "Jean Mbarga" in str(quote)


@pytest.mark.django_db
def test_quote_recalculates_totals_from_items():
    quote = make_quote()
    QuoteItem.objects.create(
        quote=quote, title="Salle", quantity=Decimal("2"), unit_price=Decimal("50000")
    )
    QuoteItem.objects.create(
        quote=quote, title="Traiteur", quantity=Decimal("1.5"), unit_price=Decimal("20100.10")
    )
    quote.refresh_from_db()
    assert quote.subtotal == Decimal("130150.15")
    assert quote.total_amount == Decimal("130150.15")


@pytest.mark.django_db
def test_total_applies_discount_and_transport():
    quote = make_quote(discount=Decimal("5000"), transport_cost=Decimal("1500"))
    QuoteItem.objects.create(
        quote=quote, title="Chapiteau", quantity=Decimal("1"), unit_price=Decimal("80000")
    )
    quote.refresh_from_db()
    assert quote.subtotal == Decimal("80000.00")
    assert quote.total_amount == Decimal("76500.00")


@pytest.mark.django_db
def test_line_total_rounds_to_two_decimals():
    quote = make_quote()
    item = QuoteItem.objects.create(
        quote=quote, title="Ligne", quantity=Decimal("1.5"), unit_price=Decimal("10.01")
    )
    assert line_total(item) == Decimal("15.02")
    assert item.total_price == Decimal("15.02")
    assert quote_total(quote) == Decimal("15.02")


@pytest.mark.django_db
def test_deleting_item_updates_totals():
    quote = make_quote()
    first = QuoteItem.objects.create(
        quote=quote, title="A", quantity=Decimal("1"), unit_price=Decimal("10000")
    )
    QuoteItem.objects.create(
        quote=quote, title="B", quantity=Decimal("1"), unit_price=Decimal("5000")
    )
    assert quote.total_amount == Decimal("15000.00")
    first.delete()
    quote.refresh_from_db()
    assert quote.total_amount == Decimal("5000.00")


@pytest.mark.django_db
def test_balance_due_subtracts_deposit():
    quote = make_quote(deposit_amount=Decimal("20000"))
    QuoteItem.objects.create(
        quote=quote, title="Traiteur", quantity=Decimal("1"), unit_price=Decimal("50000")
    )
    quote.refresh_from_db()
    assert quote.total_amount == Decimal("50000.00")
    assert quote.balance_due == Decimal("30000.00")


@pytest.mark.django_db
def test_only_draft_is_editable():
    quote = make_quote()
    assert quote.is_editable is True
    quote.status = Quote.Status.SENT
    quote.save()
    assert quote.is_editable is False


@pytest.mark.django_db
def test_status_transitions_follow_business_rules():
    from django.core.exceptions import ValidationError

    from devis.services.status import allowed_statuses, change_status

    quote = make_quote()
    assert allowed_statuses(quote) == {Quote.Status.SENT}
    with pytest.raises(ValidationError):
        change_status(quote, Quote.Status.ACCEPTED)

    change_status(quote, Quote.Status.SENT)
    change_status(quote, Quote.Status.ACCEPTED)
    change_status(quote, Quote.Status.CONVERTED)
    quote.refresh_from_db()
    assert quote.status == Quote.Status.CONVERTED
    assert allowed_statuses(quote) == set()


@pytest.mark.django_db
def test_deleting_quote_removes_items():
    quote = make_quote()
    QuoteItem.objects.create(quote=quote, title="Ligne")
    quote_id = quote.pk
    quote.delete()
    assert not QuoteItem.objects.filter(quote_id=quote_id).exists()
