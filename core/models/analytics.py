import uuid

from django.db import models


class PageView(models.Model):
    """Événement de consultation d'une page publique (suivi léger).

    Un enregistrement par page vue, et une « impression » par carte affichée
    (catégorie, réalisation, service). Aucune donnée personnelle n'est stockée.
    """

    class Kind(models.TextChoices):
        SITE = "site", "Page du site"
        CATEGORY = "category", "Catégorie"
        ACHIEVEMENT = "achievement", "Réalisation"
        SERVICE = "service", "Service"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField("type", max_length=20, choices=Kind.choices, db_index=True)
    target_id = models.UUIDField("élément", null=True, blank=True, db_index=True)
    path = models.CharField("chemin", max_length=200, blank=True)
    created_at = models.DateTimeField("consulté le", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "consultation"
        verbose_name_plural = "consultations"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["kind", "created_at"])]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} — {self.created_at:%d/%m/%Y %H:%M}"
