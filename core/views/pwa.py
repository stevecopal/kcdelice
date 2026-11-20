"""Application web installable (PWA) de l'espace d'administration.

Le manifeste et les icônes sont servis par Django pour que le nom et le logo
proviennent toujours de la fiche entreprise enregistrée en base.
"""

from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils.cache import patch_cache_control
from django.views.decorators.http import require_GET
from PIL import Image, ImageDraw, ImageFont

from core.models import Company

ICON_SIZES = (180, 192, 512)
BACKGROUND = (255, 255, 255, 0)
GREEN = (21, 163, 74, 255)


def _company() -> Company | None:
    return Company.get_solo()


def _logo_bitmap() -> Image.Image | None:
    """Logo de l'entreprise, ou None s'il n'y en a pas d'exploitable."""
    company = _company()
    if not company or not company.logo:
        return None
    try:
        with company.logo.open("rb") as handle:
            image = Image.open(handle)
            image.load()
        return image.convert("RGBA")
    except (OSError, ValueError):
        return None


def _fallback_bitmap(size: int) -> Image.Image:
    """Pastille verte avec l'initiale de l'entreprise, sans fichier média."""
    company = _company()
    letter = (company.name[:1] if company and company.name else "K").upper()
    image = Image.new("RGBA", (size, size), GREEN)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default(size=int(size * 0.5))
    except TypeError:  # Pillow sans police redimensionnable
        font = ImageFont.load_default()
    box = draw.textbbox((0, 0), letter, font=font)
    position = ((size - (box[2] - box[0])) / 2 - box[0], (size - (box[3] - box[1])) / 2 - box[1])
    draw.text(position, letter, fill=(255, 255, 255, 255), font=font)
    return image


def _icon(size: int) -> bytes:
    logo = _logo_bitmap()
    if logo is None:
        bitmap = _fallback_bitmap(size)
    else:
        side = max(logo.size)
        canvas = Image.new("RGBA", (side, side), BACKGROUND)
        canvas.paste(logo, ((side - logo.width) // 2, (side - logo.height) // 2), logo)
        bitmap = canvas.resize((size, size), Image.LANCZOS)
    buffer = BytesIO()
    bitmap.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


@require_GET
def manifest(request):
    """Manifeste de l'application : ouvre directement l'espace d'administration."""
    company = _company()
    name = company.name if company and company.name else "KCDélices"
    short_name = name if len(name) <= 12 else f"{name[:11]}…"

    response = JsonResponse(
        {
            "id": "/espace/",
            "name": f"{name} — Administration",
            "short_name": short_name,
            "description": "Gestion des devis, réalisations et services.",
            "lang": "fr",
            "dir": "ltr",
            "start_url": "/espace/",
            "scope": "/",
            "display": "standalone",
            "display_override": ["standalone", "minimal-ui"],
            "orientation": "portrait-primary",
            "background_color": "#FFFFFF",
            "theme_color": "#0B0D0F",
            "icons": [
                {
                    "src": f"/espace/icone-{size}.png",
                    "sizes": f"{size}x{size}",
                    "type": "image/png",
                    "purpose": "any",
                }
                for size in ICON_SIZES
            ]
            + [
                {
                    "src": "/espace/icone-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable",
                }
            ],
        },
        content_type="application/manifest+json",
    )
    patch_cache_control(response, public=True, max_age=3600)
    return response


@require_GET
def icon(request, size: int):
    if size not in ICON_SIZES:
        return HttpResponse(status=404)
    response = HttpResponse(_icon(size), content_type="image/png")
    patch_cache_control(response, public=True, max_age=86400)
    return response


@require_GET
def service_worker(request):
    """Service worker du site, nécessaire pour rendre la connexion installable."""
    response = TemplateResponse(
        request, "espace/service_worker.js", content_type="text/javascript"
    )
    response["Service-Worker-Allowed"] = "/"
    patch_cache_control(response, no_cache=True)
    return response


def offline(request):
    """Page de secours affichée quand le réseau est indisponible."""
    return TemplateResponse(request, "espace/offline.html", status=200)
