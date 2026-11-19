from django.views.generic import ListView

from ..models import Service


class ServicesView(ListView):
    """Liste des services actifs."""

    model = Service
    template_name = "public/services.html"
    context_object_name = "services"
    paginate_by = 9

    def get_queryset(self):
        return Service.objects.filter(is_active=True)
