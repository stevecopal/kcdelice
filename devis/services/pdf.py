"""Génération du PDF professionnel d'un devis (WeasyPrint)."""

import base64
import mimetypes

from django.template.loader import render_to_string
from django.utils import timezone

from ..models import Quote
from .calculations import line_total


def _logo_data_uri(company) -> str:
    """Encapsule le logo de l'entreprise pour que le PDF soit autonome."""
    if not company or not company.logo:
        return ""
    try:
        with company.logo.open("rb") as handle:
            content = handle.read()
    except (FileNotFoundError, OSError, ValueError):
        return ""
    mime = mimetypes.guess_type(company.logo.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(content).decode('ascii')}"


def build_pdf_context(quote: Quote) -> dict:
    from core.models import Company

    items = list(quote.items.all())
    return {
        "quote": quote,
        "company": Company.get_solo(),
        "logo_data_uri": _logo_data_uri(Company.get_solo()),
        "items": [{"obj": item, "total": line_total(item)} for item in items],
        "generated_at": timezone.localtime(),
    }


def render_quote_pdf(quote: Quote) -> bytes:
    """Rend le devis en PDF A4 (bytes)."""
    from weasyprint import HTML

    html = render_to_string("devis/quote_pdf.html", build_pdf_context(quote))
    return HTML(string=html).write_pdf()
