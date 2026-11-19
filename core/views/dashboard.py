from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from ..models import Achievement, EventCategory, Service
from .mixins import StaffRequiredMixin


class DashboardView(StaffRequiredMixin, TemplateView):
    """Tableau de bord : indicateurs simples sur les données réelles."""

    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        context["stats"] = [
            {
                "label": "Types d'événements",
                "value": EventCategory.objects.count(),
                "url": "category_list",
            },
            {
                "label": "Réalisations",
                "value": Achievement.objects.count(),
                "url": "achievement_list",
            },
            {"label": "Services", "value": Service.objects.count(), "url": "service_list"},
            {
                "label": "Utilisateurs administrateurs",
                "value": User.objects.filter(is_staff=True).count(),
                "url": None,
            },
        ]
        return context
