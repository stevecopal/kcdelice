from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from ..forms import EventCategoryForm
from ..models import EventCategory
from .mixins import StaffRequiredMixin


class CategoryListView(StaffRequiredMixin, ListView):
    """Liste des types d'événements : recherche et pagination."""

    model = EventCategory
    template_name = "espace/categories/list.html"
    context_object_name = "categories"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_query = self.request.GET.get("q", "").strip()
        if self.search_query:
            queryset = queryset.filter(name__icontains=self.search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.search_query
        context["query_string"] = f"q={self.search_query}" if self.search_query else ""
        return context


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = EventCategory
    form_class = EventCategoryForm
    template_name = "espace/categories/form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie créée avec succès.")
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = EventCategory
    form_class = EventCategoryForm
    template_name = "espace/categories/form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie modifiée avec succès.")
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = EventCategory
    template_name = "espace/categories/confirm_delete.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Impossible de supprimer : des réalisations sont rattachées à cette catégorie.",
            )
            return redirect("category_list")
        messages.success(self.request, "Catégorie supprimée avec succès.")
        return response


class CategoryToggleView(StaffRequiredMixin, View):
    """Active ou désactive une catégorie (POST uniquement)."""

    def post(self, request, pk):
        category = get_object_or_404(EventCategory, pk=pk)
        category.is_active = not category.is_active
        category.save()
        state = "activée" if category.is_active else "désactivée"
        messages.success(request, f"Catégorie {state} avec succès.")
        return redirect("category_list")

    def get(self, request, pk):
        return redirect("category_list")
