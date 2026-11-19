from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView


# Champ à label flottant : le placeholder invisible est requis par les variantes
# `peer-[:not(:placeholder-shown)]` du template.
LOGIN_INPUT_CLASSES = (
    "peer h-14 w-full rounded-lg border border-noir/20 bg-blanc px-4 pt-6 pb-2 "
    "text-base text-noir transition focus:border-2 focus:border-vert focus:outline-none"
)


class LoginView(DjangoLoginView):
    """Connexion à l'espace d'administration (nom d'utilisateur + mot de passe)."""

    template_name = "espace/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name, field in form.fields.items():
            field.widget.attrs["class"] = LOGIN_INPUT_CLASSES
            fields = {
                "username": {
                    "placeholder": " ",
                    "autocomplete": "username",
                    "autocapitalize": "none",
                },
                "password": {
                    "placeholder": " ",
                    "autocomplete": "current-password",
                },
            }
            field.widget.attrs.update(fields.get(name, {}))
        return form


class LogoutView(DjangoLogoutView):
    """Déconnexion puis retour à la page de connexion."""

    template_name = "espace/login.html"
