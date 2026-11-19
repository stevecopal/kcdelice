"""Calculs de devis : montants en Decimal, sans confiance aux données navigateur."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(item) -> Decimal:
    """Total d'une ligne : quantité × prix unitaire, arrondi au centime."""
    return quantize(item.quantity * item.unit_price)


def quote_subtotal(quote) -> Decimal:
    """Somme des lignes du devis (utilise la relation préchargée si possible)."""
    return quantize(
        sum((line_total(item) for item in quote.items.all()), ZERO)
    )


def quote_total(quote) -> Decimal:
    """Sous-total − réduction + frais de transport."""
    return quantize(quote_subtotal(quote) - quote.discount + quote.transport_cost)


def quote_balance(quote) -> Decimal:
    """Reste à régler après l'acompte prévu (l'acompte n'est pas un paiement)."""
    return quantize(quote.total_amount - quote.deposit_amount)
