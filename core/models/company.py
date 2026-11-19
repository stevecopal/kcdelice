import uuid

from django.core.exceptions import ValidationError
from django.db import models

from ..services.image import validate_image_size


class Company(models.Model):
    """Fiche unique de l'entreprise (singleton)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nom", max_length=200)
    logo = models.ImageField("logo", upload_to="company/", blank=True)
    presentation = models.TextField("présentation", blank=True)
    mission = models.TextField("mission", blank=True)
    vision = models.TextField("vision", blank=True)
    location = models.CharField("localisation", max_length=255, blank=True)
    phones = models.JSONField("numéros de contact", default=list, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=30, blank=True)
    email = models.EmailField("e-mail", blank=True)
    social_links = models.JSONField("réseaux sociaux", default=list, blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "entreprise"
        verbose_name_plural = "entreprise"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_solo(cls) -> Company | None:
        """Méthode simple pour récupérer l'entreprise depuis vues et templates."""
        return cls.objects.first()

    @property
    def phone_list(self) -> list[str]:
        return [str(phone) for phone in (self.phones or []) if phone]

    def clean(self) -> None:
        super().clean()
        validate_image_size(self.logo)
        if self._state.adding and Company.objects.exists():
            raise ValidationError("Une seule fiche entreprise est autorisée.")

    def save(self, *args, **kwargs) -> None:
        if Company.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Une seule fiche entreprise est autorisée.")
        from ..services.image import optimize_image

        if self.logo:
            self.logo = optimize_image(self.logo)
        super().save(*args, **kwargs)
