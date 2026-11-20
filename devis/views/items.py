from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView

from core.views.mixins import StaffRequiredMixin

from ..forms import QuoteItemForm
from ..models import Quote, QuoteItem


class EditableQuoteMixin:
    """Empêche toute modification des lignes d'un devis finalisé."""

    def dispatch(self, request, *args, **kwargs):
        self.quote = get_object_or_404(Quote, pk=kwargs["pk"])
        if not self.quote.is_editable:
            messages.error(request, "Ce devis n'est plus modifiable.")
            return redirect("quote_detail", pk=self.quote.pk)
        return super().dispatch(request, *args, **kwargs)


class QuoteItemCreateView(EditableQuoteMixin, StaffRequiredMixin, CreateView):
    """Ajoute une ligne à un brouillon."""

    model = QuoteItem
    form_class = QuoteItemForm
    template_name = "devis/quote_item_form.html"

    def form_valid(self, form):
        form.instance.quote = self.quote
        messages.success(self.request, "Ligne ajoutée au devis.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quote_detail", kwargs={"pk": self.quote.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quote"] = self.quote
        return context


class QuoteItemDeleteView(StaffRequiredMixin, DeleteView):
    """Supprime une ligne d'un brouillon et recalcule le devis."""

    model = QuoteItem
    template_name = "devis/quote_item_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.quote.is_editable:
            messages.error(request, "Ce devis n'est plus modifiable.")
            return redirect("quote_detail", pk=self.object.quote_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("quote_detail", kwargs={"pk": self.object.quote_id})

    def form_valid(self, form):
        messages.success(self.request, "Ligne supprimée.")
        return super().form_valid(form)
