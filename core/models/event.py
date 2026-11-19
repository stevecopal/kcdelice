import uuid

from django.db import models

from ..services.image import validate_image_size


class EventCategory(models.Model):
    """Catégorie de réalisations affichée sur l'accueil."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nom", max_length=200)
    cover_image = models.ImageField("image de couverture", upload_to="categories/", blank=True)
    is_active = models.BooleanField("active", default=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "catégorie de réalisation"
        verbose_name_plural = "catégories de réalisations"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        validate_image_size(self.cover_image)

    def save(self, *args, **kwargs) -> None:
        from ..services.image import optimize_image

        if self.cover_image and not getattr(self.cover_image, "_committed", False):
            self.cover_image = optimize_image(self.cover_image)
        super().save(*args, **kwargs)
