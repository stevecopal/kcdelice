import uuid
from decimal import Decimal

from django.db import models


class QuoteItem(models.Model):
    """Ligne chiffrée d'un devis (désignation, quantité, prix unitaire)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(
        "devis.Quote",
        verbose_name="devis",
        related_name="items",
        on_delete=models.CASCADE,
    )
    label = models.CharField("désignation", max_length=200)
    quantity = models.DecimalField(
        "quantité", max_digits=10, decimal_places=2, default=Decimal("1")
    )
    unit_price = models.DecimalField(
        "prix unitaire", max_digits=12, decimal_places=2, default=Decimal("0")
    )

    class Meta:
        verbose_name = "ligne de devis"
        verbose_name_plural = "lignes de devis"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.label
