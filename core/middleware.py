"""Suivi léger de l'activité publique.

Un enregistrement par page vue et par carte affichée (catégorie, réalisation,
service). Les membres du staff et les requêtes non-GET ne sont pas comptés, et
aucune donnée personnelle n'est conservée : uniquement le chemin et l'instant.
"""

import logging

from .models import Achievement, EventCategory, PageView, Service

logger = logging.getLogger("core")

# Pages publiques suivies → type d'événement « page du site ».
SITE_PAGES = {"home", "about", "services"}
TRACKED_VIEWS = SITE_PAGES | {"category_detail"}

# Nombre de cartes réellement affichées sur une page (pagination publique).
SERVICES_PER_PAGE = 9
ACHIEVEMENTS_PER_PAGE = 12


class PublicStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:  # pragma: no cover - le suivi ne doit jamais casser une page
            logger.exception("Suivi d'activité publique impossible")
        return response

    @staticmethod
    def _record(request, response) -> None:
        if request.method != "GET" or response.status_code != 200:
            return

        match = getattr(request, "resolver_match", None)
        view_name = getattr(match, "url_name", None)
        if view_name not in TRACKED_VIEWS:
            return

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff:
            return

        path = request.path[:200]
        events = [PageView(kind=PageView.Kind.SITE, path=path)]

        if view_name == "services":
            events += [
                PageView(kind=PageView.Kind.SERVICE, target_id=service_id, path=path)
                for service_id in Service.objects.filter(is_active=True)
                .values_list("id", flat=True)[:SERVICES_PER_PAGE]
            ]
        elif view_name == "category_detail":
            category_id = match.kwargs.get("pk")
            if category_id and EventCategory.objects.filter(pk=category_id, is_active=True).exists():
                events.append(
                    PageView(
                        kind=PageView.Kind.CATEGORY,
                        target_id=category_id,
                        path=path,
                    )
                )
                events += [
                    PageView(
                        kind=PageView.Kind.ACHIEVEMENT,
                        target_id=achievement_id,
                        path=path,
                    )
                    for achievement_id in Achievement.objects.filter(
                        category_id=category_id, is_active=True
                    ).values_list("id", flat=True)[:ACHIEVEMENTS_PER_PAGE]
                ]

        PageView.objects.bulk_create(events)
