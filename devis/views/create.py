from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView

from core.views.mixins import StaffRequiredMixin

from ..forms import QuoteForm
from ..models import Quote


class QuoteCreateView(StaffRequiredMixin, CreateView):
    """Création d'un devis bref (client facultatif)."""

    model = Quote
    form_class = QuoteForm
    template_name = "devis/quote_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Devis créé avec succès.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quote_detail", kwargs={"pk": self.object.pk})
