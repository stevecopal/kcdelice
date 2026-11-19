import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Quote(models.Model):
    """Devis bref : titre, client optionnel, lignes chiffrées."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("titre", max_length=200)
    client_name = models.CharField("nom du client", max_length=200, blank=True)
    client_phone = models.CharField("téléphone du client", max_length=40, blank=True)
    client_email = models.EmailField("e-mail du client", blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "devis"
        verbose_name_plural = "devis"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        client = f" — {self.client_name}" if self.client_name else ""
        return f"{self.title}{client}"

    @property
    def has_client(self) -> bool:
        return bool(self.client_name or self.client_phone or self.client_email)

    @property
    def total(self):
        from ..services.calculations import quote_total

        return quote_total(self)
