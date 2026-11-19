"""Règles métier de changement de statut d'un devis."""

from django.core.exceptions import ValidationError

from ..models import Quote

TRANSITIONS = {
    Quote.Status.DRAFT: {Quote.Status.SENT},
    Quote.Status.SENT: {Quote.Status.ACCEPTED, Quote.Status.REFUSED, Quote.Status.DRAFT},
    Quote.Status.ACCEPTED: {Quote.Status.CONVERTED, Quote.Status.REFUSED},
    Quote.Status.REFUSED: {Quote.Status.SENT},
    Quote.Status.CONVERTED: set(),
}


def allowed_statuses(quote: Quote):
    """Statuts accessibles depuis le statut courant."""
    return TRANSITIONS.get(quote.status, set())


def can_change_status(quote: Quote, new_status: str) -> bool:
    return new_status in allowed_statuses(quote)


def change_status(quote: Quote, new_status: str) -> Quote:
    """Applique une transition autorisée, sinon lève une ValidationError."""
    if new_status not in Quote.Status.values:
        raise ValidationError("Statut de devis inconnu.")
    if not can_change_status(quote, new_status):
        raise ValidationError(
            f"Transition impossible : {quote.get_status_display()} → "
            f"{Quote.Status(new_status).label}."
        )
    quote.status = new_status
    quote.save(update_fields=["status", "updated_at"])
    return quote
