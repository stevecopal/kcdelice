import uuid

from django.db import models


class Achievement(models.Model):
    """Réalisation rattachée à une catégorie."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("titre", max_length=200)
    category = models.ForeignKey(
        "core.EventCategory",
        verbose_name="catégorie",
        related_name="achievements",
        on_delete=models.PROTECT,
    )
    is_active = models.BooleanField("active", default=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "réalisation"
        verbose_name_plural = "réalisations"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def main_image(self):
        """Image principale (première de la galerie), sans requête supplémentaire."""
        images = list(self.images.all())
        return images[0] if images else None
