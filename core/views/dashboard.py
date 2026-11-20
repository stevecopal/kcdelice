from django.contrib.auth import get_user_model
from django.db.models import Count
from django.views.generic import TemplateView

from devis.models import Quote

from ..models import Achievement, EventCategory, PageView, Service
from .mixins import StaffRequiredMixin


class DashboardView(StaffRequiredMixin, TemplateView):
    """Tableau de bord : indicateurs calculés depuis les données réelles."""

    template_name = "espace/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()

        kinds = PageView.Kind
        page_counts = dict(
            PageView.objects.values("kind").annotate(total=Count("id")).values_list("kind", "total")
        )

        context["stats"] = [
            {
                "label": "Devis",
                "value": Quote.objects.count(),
                "url": "quote_list",
            },
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

        context["public_stats"] = {
            "visits": page_counts.get(kinds.SITE, 0),
            "categories": page_counts.get(kinds.CATEGORY, 0),
            "achievements": page_counts.get(kinds.ACHIEVEMENT, 0),
            "services": page_counts.get(kinds.SERVICE, 0),
        }
        context["top_achievements"] = self._top_items(
            kinds.ACHIEVEMENT, Achievement, select_related=("category",)
        )
        context["top_services"] = self._top_items(kinds.SERVICE, Service)
        return context

    @staticmethod
    def _top_items(kind: str, model, select_related=(), limit: int = 5) -> list[dict]:
        """Éléments les plus consultés, avec leur part relative au premier."""
        rows = list(
            PageView.objects.filter(kind=kind, target_id__isnull=False)
            .values("target_id")
            .annotate(total=Count("id"))
            .order_by("-total")[: limit * 2]
        )
        if not rows:
            return []

        queryset = model.objects.filter(pk__in=[row["target_id"] for row in rows])
        if select_related:
            queryset = queryset.select_related(*select_related)
        objects = {obj.pk: obj for obj in queryset}

        best = max(row["total"] for row in rows) or 1
        items = []
        for row in rows:
            obj = objects.get(row["target_id"])
            if obj is None:
                continue
            items.append(
                {
                    "object": obj,
                    "count": row["total"],
                    "percent": round(row["total"] * 100 / best),
                }
            )
        return items[:limit]
