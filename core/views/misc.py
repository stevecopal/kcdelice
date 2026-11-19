"""Écrans transitoires et paramètres du compte administrateur."""

from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from ..forms import StyledPasswordChangeForm
from .mixins import StaffRequiredMixin


class ClientsView(StaffRequiredMixin, TemplateView):
    """Gestion des clients : écran d'attente propre (phase 3)."""

    template_name = "espace/placeholder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Clients"
        context["placeholder_text"] = (
            "La gestion des clients sera disponible prochainement."
        )
        return context


class SettingsView(StaffRequiredMixin, PasswordChangeView):
    """Paramètres : changement du mot de passe du compte."""

    template_name = "espace/settings.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("settings")

    def form_valid(self, form):
        messages.success(self.request, "Mot de passe modifié avec succès.")
        return super().form_valid(form)
