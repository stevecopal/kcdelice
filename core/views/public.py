from django.views.generic import ListView

from ..models import EventCategory


class HomeView(ListView):
    """Accueil : catégories de réalisations actives."""

    model = EventCategory
    template_name = "public/home.html"
    context_object_name = "categories"
    paginate_by = 12

    def get_queryset(self):
        return EventCategory.objects.filter(is_active=True)
