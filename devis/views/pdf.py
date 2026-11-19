from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

from ..models import Quote
from ..services.pdf import render_quote_pdf


class QuotePDFView(LoginRequiredMixin, View):
    """Télécharge le devis au format PDF."""

    def get(self, request, pk):
        quote = get_object_or_404(Quote.objects.prefetch_related("items"), pk=pk)
        pdf = render_quote_pdf(quote)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="Devis-{quote.reference}.pdf"'
        )
        return response
