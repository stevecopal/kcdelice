from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DeleteView, DetailView

from core.views.mixins import StaffRequiredMixin

from ..models import Quote
from ..services.calculations import line_total, quote_balance
from ..services.status import allowed_statuses, change_status


class QuoteDetailView(StaffRequiredMixin, DetailView):
    """Détail d'un devis : client, événement, lignes, montants et actions."""

    model = Quote
    template_name = "devis/quote_detail.html"
    context_object_name = "quote"

    def get_queryset(self):
        return Quote.objects.prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = [
            {"obj": item, "total": line_total(item)} for item in self.object.items.all()
        ]
        context["balance"] = quote_balance(self.object)
        context["next_statuses"] = [
            {"value": value, "label": Quote.Status(value).label}
            for value in allowed_statuses(self.object)
        ]
        return context


class QuoteStatusUpdateView(StaffRequiredMixin, View):
    """Change le statut d'un devis selon les transitions autorisées."""

    def post(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        new_status = request.POST.get("status", "")
        try:
            change_status(quote, new_status)
        except ValidationError as error:
            messages.error(request, error.messages[0])
        else:
            messages.success(
                request,
                f"Le devis est maintenant « {quote.get_status_display()} ».",
            )
        return redirect("quote_detail", pk=quote.pk)


class QuoteDeleteView(StaffRequiredMixin, DeleteView):
    """Supprime un devis, uniquement s'il est encore au brouillon."""

    model = Quote
    template_name = "devis/quote_confirm_delete.html"
    context_object_name = "quote"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_editable:
            messages.error(request, "Seul un brouillon peut être supprimé.")
            return redirect("quote_detail", pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("quote_list")

    def form_valid(self, form):
        reference = self.object.reference
        messages.success(self.request, f"Devis {reference} supprimé.")
        return super().form_valid(form)
