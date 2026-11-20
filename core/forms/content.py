"""Formulaires de gestion des contenus (catégories, réalisations, services)."""

from django import forms
from django.forms import inlineformset_factory

from ..models import Achievement, AchievementImage, EventCategory, Service

INPUT_CLASSES = (
    "w-full rounded-xl border border-noir/20 bg-blanc px-4 py-3 text-noir "
    "placeholder:text-noir/50 transition focus:border-vert"
)
FILE_CLASSES = "w-full rounded-xl border border-noir/20 bg-blanc px-4 py-3 text-noir file:mr-4 file:rounded-full file:border-0 file:bg-vert file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blanc"
CHECKBOX_CLASSES = "h-5 w-5 rounded border-noir/30 text-vert accent-vert focus:ring-vert"


class ImageFileInput(forms.ClearableFileInput):
    """Champ fichier : uniquement le sélecteur, sans texte technique de Django."""

    template_name = "espace/includes/file_input.html"


class EventCategoryForm(forms.ModelForm):
    """Création / modification d'un type d'événement."""

    class Meta:
        model = EventCategory
        fields = ["name", "cover_image", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Ex. : Mariages",
                    "class": INPUT_CLASSES,
                }
            ),
            "cover_image": ImageFileInput(
                attrs={"class": FILE_CLASSES, "accept": "image/*", "data-preview": "category-cover"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
        }


class AchievementForm(forms.ModelForm):
    """Création / modification d'une réalisation."""

    class Meta:
        model = Achievement
        fields = ["title", "category", "is_active"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Ex. : Mariage Aïcha", "class": INPUT_CLASSES}
            ),
            "category": forms.Select(attrs={"class": INPUT_CLASSES}),
            "is_active": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
        }


class AchievementImageForm(forms.ModelForm):
    """Une image de galerie : fichier obligatoire à la création, optionnel à l'édition."""

    class Meta:
        model = AchievementImage
        fields = ["image"]
        widgets = {
            "image": ImageFileInput(
                attrs={"class": FILE_CLASSES, "accept": "image/*"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["image"].required = False


AchievementImageFormSet = inlineformset_factory(
    Achievement,
    AchievementImage,
    form=AchievementImageForm,
    fields=["image"],
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class ServiceForm(forms.ModelForm):
    """Création / modification d'un service."""

    class Meta:
        model = Service
        fields = ["title", "cover_image", "description", "is_active"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Ex. : Décoration de salle", "class": INPUT_CLASSES}
            ),
            "cover_image": ImageFileInput(
                attrs={"class": FILE_CLASSES, "accept": "image/*", "data-preview": "service-cover"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Décrivez brièvement la prestation…",
                    "class": INPUT_CLASSES,
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
        }
