"""Formulaires d'authentification de l'espace d'administration."""

from django.contrib.auth.forms import PasswordChangeForm

from .content import INPUT_CLASSES


class StyledPasswordChangeForm(PasswordChangeForm):
    """Changement de mot de passe avec les champs de la charte.

    Les consignes techniques de Django ne sont plus imprimées : la page les
    présente sous forme de validation en direct (voir static/js/password.js).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "old_password": "Mot de passe actuel",
            "new_password1": "Nouveau mot de passe",
            "new_password2": "Confirmation du nouveau mot de passe",
        }
        autocomplete = {
            "old_password": "current-password",
            "new_password1": "new-password",
            "new_password2": "new-password",
        }
        for name, field in self.fields.items():
            field.help_text = ""
            field.widget.attrs.update(
                {
                    "class": INPUT_CLASSES,
                    "autocomplete": autocomplete.get(name, "off"),
                }
            )
            if name in labels:
                field.label = labels[name]
