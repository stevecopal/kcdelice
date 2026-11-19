"""Vérifie que l'environnement de test pytest-django est opérationnel."""

import django
import pytest
from django.conf import settings


@pytest.mark.django_db
def test_django_environment_is_ready():
    assert settings.configured
    assert django.get_version().startswith("6.1.")
    assert "django.contrib.auth" in settings.INSTALLED_APPS
