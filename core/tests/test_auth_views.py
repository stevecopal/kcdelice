"""Tests de l'authentification de l'espace d'administration."""

import pytest

@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", password="Pass1234!", is_staff=True
    )


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(
        username="visiteur", password="Pass1234!"
    )


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get("/espace/")
    assert response.status_code == 302
    assert response["Location"].startswith("/connexion/")
    assert "next=/espace/" in response["Location"]


@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get("/connexion/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Bienvenue !" in body
    assert "Continuer" in body
    assert "Retour au site" in body


@pytest.mark.django_db
def test_login_success_redirects_to_dashboard(client, staff_user):
    response = client.post(
        "/connexion/", {"username": "staff", "password": "Pass1234!"}
    )
    assert response.status_code == 302
    assert response["Location"].endswith("/espace/")


@pytest.mark.django_db
def test_login_invalid_credentials_shows_error(client, staff_user):
    response = client.post(
        "/connexion/", {"username": "staff", "password": "mauvais"}
    )
    assert response.status_code == 200
    form = response.context["form"]
    assert form.non_field_errors() or form.errors


@pytest.mark.django_db
def test_logout_posts_and_redirects_to_login(client, staff_user):
    client.force_login(staff_user)
    response = client.post("/deconnexion/")
    assert response.status_code == 302
    assert response["Location"].endswith("/connexion/")


@pytest.mark.django_db
def test_authenticated_user_is_redirected_away_from_login(client, staff_user):
    client.force_login(staff_user)
    response = client.get("/connexion/")
    assert response.status_code == 302
    assert response["Location"].endswith("/espace/")


@pytest.mark.django_db
def test_regular_user_gets_403_on_dashboard(client, regular_user):
    client.force_login(regular_user)
    response = client.get("/espace/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_regular_user_gets_403_on_category_list(client, regular_user):
    client.force_login(regular_user)
    response = client.get("/espace/types-evenements/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_category_list_redirects_to_login(client):
    response = client.get("/espace/types-evenements/")
    assert response.status_code == 302
    assert "/connexion/" in response["Location"]
