import uuid

from django.db import models

from ..services.image import validate_image_size


class Service(models.Model):
    """Service proposé par l'entreprise."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("titre", max_length=200)
    cover_image = models.ImageField("image de couverture", upload_to="services/", blank=True)
    description = models.TextField("description", blank=True)
    is_active = models.BooleanField("actif", default=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        validate_image_size(self.cover_image)

    def save(self, *args, **kwargs) -> None:
        from ..services.image import optimize_image

        if self.cover_image and not getattr(self.cover_image, "_committed", False):
            self.cover_image = optimize_image(self.cover_image)
        super().save(*args, **kwargs)
