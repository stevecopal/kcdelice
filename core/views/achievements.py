from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.list import MultipleObjectMixin

from ..forms import AchievementForm, AchievementImageFormSet
from ..models import Achievement, EventCategory
from .mixins import StaffRequiredMixin


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


class AchievementListView(StaffRequiredMixin, ListView):
    """Liste des réalisations : recherche, filtre par catégorie, pagination."""

    model = Achievement
    template_name = "espace/achievements/list.html"
    context_object_name = "achievements"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category").prefetch_related("images")
        self.search_query = self.request.GET.get("q", "").strip()
        self.category_filter = self.request.GET.get("categorie", "").strip()
        if self.search_query:
            queryset = queryset.filter(title__icontains=self.search_query)
        if self.category_filter:
            queryset = queryset.filter(category_id=self.category_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.search_query
        context["categories"] = EventCategory.objects.all()
        context["selected_category"] = self.category_filter
        parts = []
        if self.search_query:
            parts.append(f"q={self.search_query}")
        if self.category_filter:
            parts.append(f"categorie={self.category_filter}")
        context["query_string"] = "&".join(parts)
        return context


class AchievementFormsetMixin:
    """Ajoute le formset d'images (création et édition) au formulaire."""

    template_name = "espace/achievements/form.html"

    def get_image_instance(self):
        return getattr(self, "object", None) or Achievement()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_image_instance()
        if self.request.method == "POST":
            context["image_formset"] = AchievementImageFormSet(
                self.request.POST, self.request.FILES, instance=instance
            )
        else:
            context["image_formset"] = AchievementImageFormSet(instance=instance)
        context["categories"] = EventCategory.objects.all()
        return context


class AchievementCreateView(AchievementFormsetMixin, StaffRequiredMixin, CreateView):
    model = Achievement
    form_class = AchievementForm
    success_url = reverse_lazy("achievement_list")

    def form_valid(self, form):
        achievement = form.save(commit=False)
        formset = AchievementImageFormSet(
            self.request.POST, self.request.FILES, instance=achievement
        )
        if not formset.is_valid():
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
        achievement.save()
        self.object = achievement
        formset.instance = achievement
        formset.save()
        messages.success(self.request, "Réalisation créée avec succès.")
        return HttpResponseRedirect(self.get_success_url())


class AchievementUpdateView(AchievementFormsetMixin, StaffRequiredMixin, UpdateView):
    model = Achievement
    form_class = AchievementForm
    success_url = reverse_lazy("achievement_list")

    def form_valid(self, form):
        formset = AchievementImageFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )
        if not formset.is_valid():
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, "Réalisation modifiée avec succès.")
        return HttpResponseRedirect(self.get_success_url())


class AchievementDeleteView(StaffRequiredMixin, DeleteView):
    model = Achievement
    template_name = "espace/achievements/confirm_delete.html"
    success_url = reverse_lazy("achievement_list")

    def form_valid(self, form):
        messages.success(self.request, "Réalisation supprimée avec succès.")
        return super().form_valid(form)


class AchievementToggleView(StaffRequiredMixin, View):
    """Active ou désactive une réalisation (POST uniquement)."""

    def post(self, request, pk):
        achievement = get_object_or_404(Achievement, pk=pk)
        achievement.is_active = not achievement.is_active
        achievement.save()
        state = "activée" if achievement.is_active else "désactivée"
        messages.success(request, f"Réalisation {state} avec succès.")
        return redirect("achievement_list")

    def get(self, request, pk):
        return redirect("achievement_list")
