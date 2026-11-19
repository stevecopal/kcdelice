from django.views.generic import TemplateView

from ..models import Company


class AboutView(TemplateView):
    """À propos : sections renseignées uniquement."""

    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = Company.get_solo()
        return context
