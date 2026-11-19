import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Quote(models.Model):
    """Devis : identité client, informations d'événement et montants recalculés."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        SENT = "sent", "Envoyé"
        ACCEPTED = "accepted", "Accepté"
        REFUSED = "refused", "Refusé"
        CONVERTED = "converted", "Commande"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(
        "référence", max_length=30, unique=True, blank=True, editable=False
    )
    title = models.CharField("objet", max_length=200, blank=True)

    client_name = models.CharField("nom du client", max_length=200)
    client_phone = models.CharField("téléphone du client", max_length=40)
    client_email = models.EmailField("e-mail du client", blank=True)
    client_address = models.CharField("adresse du client", max_length=255, blank=True)

    event_date = models.DateField("date de l'événement", null=True, blank=True)
    event_location = models.CharField("lieu de l'événement", max_length=255)

    subtotal = models.DecimalField(
        "sous-total", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    discount = models.DecimalField(
        "réduction",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    transport_cost = models.DecimalField(
        "frais de transport",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_amount = models.DecimalField(
        "montant total", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    deposit_amount = models.DecimalField(
        "acompte prévu",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    status = models.CharField(
        "statut", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    valid_until = models.DateField("valable jusqu'au", null=True, blank=True)
    notes = models.TextField("conditions particulières", blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "devis"
        verbose_name_plural = "devis"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount__gte=0),
                name="quote_discount_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(transport_cost__gte=0),
                name="quote_transport_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(deposit_amount__gte=0),
                name="quote_deposit_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reference or 'Devis'} — {self.client_name}"

    def save(self, *args, **kwargs) -> None:
        if not self.reference:
            from ..services.references import generate_reference

            self.reference = generate_reference()
        super().save(*args, **kwargs)

    @property
    def is_editable(self) -> bool:
        """Seul un brouillon peut encore être modifié."""
        return self.status == self.Status.DRAFT

    @property
    def is_finalized(self) -> bool:
        return not self.is_editable

    @property
    def has_client(self) -> bool:
        return bool(self.client_name or self.client_phone or self.client_email)

    @property
    def balance_due(self) -> Decimal:
        """Reste à régler après l'acompte prévu (aucun paiement encaissé ici)."""
        return self.total_amount - self.deposit_amount

    @property
    def items_count(self) -> int:
        return self.items.count()

    def recalculate(self, save: bool = True) -> "Quote":
        """Recalcule sous-total et total côté serveur depuis les lignes en base."""
        subtotal = sum(
            (item.total_price for item in self.items.all()), Decimal("0.00")
        )
        self.subtotal = subtotal
        self.total_amount = subtotal - self.discount + self.transport_cost
        if save:
            self.save(
                update_fields=[
                    "subtotal",
                    "total_amount",
                    "discount",
                    "transport_cost",
                    "deposit_amount",
                    "updated_at",
                ]
            )
        return self
