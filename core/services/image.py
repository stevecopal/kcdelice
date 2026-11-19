"""Optimisation et validation des images."""

import io

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 Mo
MAX_WIDTH = 1600


def validate_image_size(image) -> None:
    """Refuse les fichiers trop lourds ou illisibles (appelé par model.clean)."""
    if not image:
        return
    if getattr(image, "size", 0) > MAX_IMAGE_SIZE:
        raise ValidationError(
            f"L'image dépasse la taille maximale de {MAX_IMAGE_SIZE // (1024 * 1024)} Mo."
        )
    try:
        if hasattr(image, "seek"):
            image.seek(0)
        img = Image.open(image)
        img.verify()
        if hasattr(image, "seek"):
            image.seek(0)
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError("Le fichier n'est pas une image valide.")


def optimize_image(image, max_width: int = MAX_WIDTH):
    """Redimensionne les images trop larges ; laisse le reste intact."""
    if not image:
        return image
    try:
        if hasattr(image, "seek"):
            image.seek(0)
        img = Image.open(image)
        img.load()
    except (UnidentifiedImageError, OSError, ValueError):
        if hasattr(image, "seek"):
            try:
                image.seek(0)
            except (OSError, ValueError):
                pass
        return image

    if img.width <= max_width:
        if hasattr(image, "seek"):
            try:
                image.seek(0)
            except (OSError, ValueError):
                pass
        return image

    ratio = max_width / img.width
    resized = img.resize((max_width, max(1, int(img.height * ratio))), Image.LANCZOS)

    fmt = (img.format or "JPEG").upper()
    if fmt in ("JPEG", "JPG"):
        fmt = "JPEG"
    elif fmt not in ("PNG", "WEBP"):
        return image

    buffer = io.BytesIO()
    if fmt == "JPEG":
        resized.save(buffer, "JPEG", quality=85, optimize=True)
    elif fmt == "PNG":
        resized.save(buffer, "PNG", optimize=True)
    else:
        resized.save(buffer, "WEBP", quality=85)

    name = getattr(image, "name", "image") or "image"
    return ContentFile(buffer.getvalue(), name=name)
