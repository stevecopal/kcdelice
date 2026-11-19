from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from ..models import Quote


class QuoteListView(LoginRequiredMixin, ListView):
    """Liste des devis (espace privé)."""

    model = Quote
    template_name = "devis/quote_list.html"
    context_object_name = "quotes"
    paginate_by = 10
    login_url = "admin:login"

    def get_queryset(self):
        return Quote.objects.prefetch_related("items")
