from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView

from ..models import Quote


class QuoteListView(LoginRequiredMixin, ListView):
    """Liste des devis avec recherche par référence/client et filtre par statut."""

    model = Quote
    template_name = "devis/quote_list.html"
    context_object_name = "quotes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Quote.objects.all()
        self.search = (self.request.GET.get("q") or "").strip()
        self.status = (self.request.GET.get("status") or "").strip()

        if self.search:
            queryset = queryset.filter(
                Q(reference__icontains=self.search)
                | Q(client_name__icontains=self.search)
                | Q(client_phone__icontains=self.search)
                | Q(event_location__icontains=self.search)
                | Q(title__icontains=self.search)
            )
        if self.status in Quote.Status.values:
            queryset = queryset.filter(status=self.status)
        return queryset

    def render_to_response(self, context, **response_kwargs):
        """Filtres AJAX : ne renvoyer que le bloc de résultats."""
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(self.request, "devis/_quote_results.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = {}
        if self.search:
            params["q"] = self.search
        if self.status in Quote.Status.values:
            params["status"] = self.status
        context.update(
            {
                "q": self.search,
                "selected_status": self.status,
                "statuses": Quote.Status.choices,
                "has_filters": bool(params),
                "query_string": urlencode(params),
            }
        )
        return context
