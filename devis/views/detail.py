from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView

from ..forms import QuoteItemForm
from ..models import Quote, QuoteItem
from ..services.calculations import line_total


class QuoteDetailView(LoginRequiredMixin, DetailView):
    """Détail d'un devis : lignes, total, ajout de ligne."""

    model = Quote
    template_name = "devis/quote_detail.html"
    context_object_name = "quote"

    def get_queryset(self):
        return Quote.objects.prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(self.object.items.all())
        context["items"] = [
            {"obj": item, "total": line_total(item)} for item in items
        ]
        context["total"] = self.object.total
        return context


class QuoteItemCreateView(LoginRequiredMixin, CreateView):
    """Ajout d'une ligne à un devis."""

    model = QuoteItem
    form_class = QuoteItemForm
    template_name = "devis/quote_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.quote = get_object_or_404(Quote, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

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


class QuoteItemDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'une ligne de devis."""

    model = QuoteItem
    template_name = "devis/quote_item_confirm_delete.html"

    def get_success_url(self):
        return reverse("quote_detail", kwargs={"pk": self.object.quote_id})

    def form_valid(self, form):
        messages.success(self.request, "Ligne supprimée.")
        return super().form_valid(form)
