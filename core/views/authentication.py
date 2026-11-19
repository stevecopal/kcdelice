from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from ..forms.content import INPUT_CLASSES


class LoginView(DjangoLoginView):
    """Connexion à l'espace d'administration (nom d'utilisateur + mot de passe)."""

    template_name = "admin/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASSES)
        return form


class LogoutView(DjangoLogoutView):
    """Déconnexion puis retour à la page de connexion."""

    template_name = "admin/login.html"
