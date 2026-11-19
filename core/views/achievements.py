from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.list import MultipleObjectMixin

from ..models import Achievement, EventCategory


class CategoryDetailView(MultipleObjectMixin, DetailView):
    """Galerie des réalisations d'une catégorie active."""

    model = EventCategory
    template_name = "public/category.html"
    context_object_name = "category"
    paginate_by = 12

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404("Catégorie introuvable.")
        return obj

    def get_context_object_name(self, object_list):
        return "achievements"

    def get_context_data(self, **kwargs):
        self.object_list = (
            Achievement.objects.filter(category=self.object, is_active=True)
            .prefetch_related("images")
        )
        context = super().get_context_data(**kwargs)
        context["category"] = self.object
        context["gallery_data"] = [
            {
                "id": str(achievement.id),
                "title": achievement.title,
                "images": [image.image.url for image in achievement.images.all()],
            }
            for achievement in context["achievements"]
        ]
        return context
