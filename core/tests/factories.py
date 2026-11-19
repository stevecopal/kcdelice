"""Fabrique de fichiers image pour les tests."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def make_image(
    name: str = "test.jpg",
    size: tuple[int, int] = (100, 80),
    fmt: str = "JPEG",
    color: tuple[int, int, int] = (21, 163, 74),
) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format=fmt)
    content_type = "image/jpeg" if fmt == "JPEG" else f"image/{fmt.lower()}"
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


def image_bytes(size: tuple[int, int] = (100, 80), fmt: str = "JPEG") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size).save(buffer, format=fmt)
    return buffer.getvalue()
