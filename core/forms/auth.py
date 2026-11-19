"""Formulaires d'authentification de l'espace d'administration."""

from django.contrib.auth.forms import PasswordChangeForm

from .content import INPUT_CLASSES


class StyledPasswordChangeForm(PasswordChangeForm):
    """Changement de mot de passe avec les champs de la charte."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES
            if getattr(field.widget, "input_type", "") == "password":
                field.widget.attrs["autocomplete"] = "current-password"
