import uuid

from django.db import models

from ..services.image import validate_image_size


class AchievementImage(models.Model):
    """Image d'une réalisation (galerie)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    achievement = models.ForeignKey(
        "core.Achievement",
        verbose_name="réalisation",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField("image", upload_to="achievements/images/")
    created_at = models.DateTimeField("créé le", auto_now_add=True)

    class Meta:
        verbose_name = "image de réalisation"
        verbose_name_plural = "images de réalisations"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Image de {self.achievement.title}"

    def clean(self) -> None:
        super().clean()
        validate_image_size(self.image)

    def save(self, *args, **kwargs) -> None:
        from ..services.image import optimize_image

        if self.image:
            self.image = optimize_image(self.image)
        super().save(*args, **kwargs)
