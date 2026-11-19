"""Restrictions d'accès aux pages d'administration (Django auth + permissions)."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réservé aux comptes actifs marqués ``is_staff`` (Django auth).

    - anonyme → redirection vers la page de connexion ;
    - connecté sans droits → 403.
    """

    login_url = "login"

    def test_func(self):
        user = self.request.user
        return user.is_active and user.is_staff
