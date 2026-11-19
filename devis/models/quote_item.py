import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class QuoteItem(models.Model):
    """Ligne chiffrée d'un devis (désignation libre, quantité, prix unitaire)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(
        "devis.Quote",
        verbose_name="devis",
        related_name="items",
        on_delete=models.CASCADE,
    )
    title = models.CharField("désignation", max_length=200)
    quantity = models.DecimalField(
        "quantité",
        max_digits=10,
        decimal_places=2,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    unit_price = models.DecimalField(
        "prix unitaire",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    total_price = models.DecimalField(
        "total de la ligne",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        verbose_name = "ligne de devis"
        verbose_name_plural = "lignes de devis"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="quote_item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0),
                name="quote_item_unit_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def compute_total(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def save(self, *args, **kwargs) -> None:
        self.total_price = self.compute_total()
        super().save(*args, **kwargs)
        self.quote.recalculate()

    def delete(self, *args, **kwargs):
        quote = self.quote
        result = super().delete(*args, **kwargs)
        quote.recalculate()
        return result

    @property
    def is_locked(self) -> bool:
        return self.quote_id and not self.quote.is_editable
