from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from ..forms import ServiceForm
from ..models import Service
from .mixins import StaffRequiredMixin


class ServicesView(ListView):
    """Liste des services actifs (public)."""

    model = Service
    template_name = "public/services.html"
    context_object_name = "services"
    paginate_by = 9

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class ServiceListView(StaffRequiredMixin, ListView):
    """Liste des services : recherche et pagination."""

    model = Service
    template_name = "espace/services/list.html"
    context_object_name = "services"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_query = self.request.GET.get("q", "").strip()
        if self.search_query:
            queryset = queryset.filter(title__icontains=self.search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.search_query
        context["query_string"] = f"q={self.search_query}" if self.search_query else ""
        return context


class ServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "espace/services/form.html"
    success_url = reverse_lazy("service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service créé avec succès.")
        return super().form_valid(form)


class ServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "espace/services/form.html"
    success_url = reverse_lazy("service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service modifié avec succès.")
        return super().form_valid(form)


class ServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Service
    template_name = "espace/services/confirm_delete.html"
    success_url = reverse_lazy("service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service supprimé avec succès.")
        return super().form_valid(form)


class ServiceToggleView(StaffRequiredMixin, View):
    """Active ou désactive un service (POST uniquement)."""

    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.is_active = not service.is_active
        service.save()
        state = "activé" if service.is_active else "désactivé"
        messages.success(request, f"Service {state} avec succès.")
        return redirect("service_list")

    def get(self, request, pk):
        return redirect("service_list")
