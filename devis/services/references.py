"""Génération des références de devis, uniques et lisibles."""

from django.db import transaction
from django.utils import timezone

REFERENCE_PREFIX = "DEV"


def _next_sequence(year: int) -> int:
    from ..models import Quote

    prefix = f"{REFERENCE_PREFIX}-{year}-"
    last = (
        Quote.objects.select_for_update()
        .filter(reference__startswith=prefix)
        .order_by("-reference")
        .values_list("reference", flat=True)
        .first()
    )
    if not last:
        return 1
    try:
        return int(last.rsplit("-", 1)[1]) + 1
    except (IndexError, ValueError):
        return Quote.objects.filter(reference__startswith=prefix).count() + 1


def generate_reference(year: int | None = None) -> str:
    """Référence au format ``DEV-2026-0001``, séquentielle par année."""
    year = year or timezone.localdate().year
    with transaction.atomic():
        sequence = _next_sequence(year)
    return f"{REFERENCE_PREFIX}-{year}-{sequence:04d}"
