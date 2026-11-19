from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from ..forms import CompanyForm
from ..models import Company
from .mixins import StaffRequiredMixin


class AboutView(TemplateView):
    """À propos : sections renseignées uniquement."""

    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = Company.get_solo()
        return context


class CompanyUpdateView(StaffRequiredMixin, UpdateView):
    """Formulaire unique de la fiche entreprise (création si absente)."""

    model = Company
    form_class = CompanyForm
    template_name = "admin/company_form.html"

    def get_object(self, queryset=None):
        return Company.get_solo() or Company()

    def form_valid(self, form):
        messages.success(self.request, "Informations de l'entreprise mises à jour avec succès.")
        return super().form_valid(form)

    success_url = reverse_lazy("company_update")
