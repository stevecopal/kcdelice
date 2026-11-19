"""Calculs de devis : totaux en Decimal, sans requête supplémentaire."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def line_total(item) -> Decimal:
    return (item.quantity * item.unit_price).quantize(CENT, rounding=ROUND_HALF_UP)


def quote_total(quote) -> Decimal:
    """Total du devis à partir des lignes déjà préchargées (pas de N+1)."""
    items = list(quote.items.all())
    total = sum((line_total(item) for item in items), Decimal("0.00"))
    return total.quantize(CENT, rounding=ROUND_HALF_UP)
