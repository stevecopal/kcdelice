"""Tests de l'espace d'administration : tableau de bord et CRUD complets."""

import pytest

from core.models import Achievement, Company, EventCategory, Service

from .factories import make_image


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", password="Pass1234!", is_staff=True
    )


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user)
    return client


@pytest.fixture
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


def image_formset(extra_images=0, initial=0, existing_ids=None):
    """Données de gestion du formset d'images."""
    existing_ids = existing_ids or []
    total = initial + extra_images
    data = {
        "images-TOTAL_FORMS": str(total),
        "images-INITIAL_FORMS": str(initial),
        "images-MIN_NUM_FORMS": "0",
        "images-MAX_NUM_FORMS": "1000",
    }
    for index in range(total):
        if index < len(existing_ids):
            data[f"images-{index}-id"] = str(existing_ids[index])
        else:
            data[f"images-{index}-id"] = ""
    return data


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_dashboard_shows_real_counts(staff_client):
    category = EventCategory.objects.create(name="Galerie")
    Achievement.objects.create(title="R1", category=category)
    Achievement.objects.create(title="R2", category=category)
    Service.objects.create(title="S1")

    response = staff_client.get("/espace/")
    assert response.status_code == 200
    stats = {stat["label"]: stat["value"] for stat in response.context["stats"]}
    assert stats["Types d'événements"] == 1
    assert stats["Réalisations"] == 2
    assert stats["Services"] == 1


@pytest.mark.django_db
def test_dashboard_requires_staff(client, django_user_model):
    user = django_user_model.objects.create_user(username="hors", password="x")
    client.force_login(user)
    assert client.get("/espace/").status_code == 403


# ---------------------------------------------------------------------------
# Types d'événements
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_category_create_update_toggle_delete(staff_client):
    response = staff_client.post(
        "/espace/types-evenements/nouveau/",
        {"name": "Mariages", "is_active": "on"},
        follow=True,
    )
    assert "Catégorie créée avec succès." in response.content.decode()
    category = EventCategory.objects.get(name="Mariages")
    assert category.is_active

    response = staff_client.post(
        f"/espace/types-evenements/{category.pk}/modifier/",
        {"name": "Mariages & Fiançailles", "is_active": "on"},
        follow=True,
    )
    assert "Catégorie modifiée avec succès." in response.content.decode()
    category.refresh_from_db()
    assert category.name == "Mariages & Fiançailles"

    response = staff_client.post(f"/espace/types-evenements/{category.pk}/basculer/", {}, follow=True)
    category.refresh_from_db()
    assert category.is_active is False
    assert "Catégorie désactivée avec succès." in response.content.decode()

    response = staff_client.post(f"/espace/types-evenements/{category.pk}/supprimer/", {}, follow=True)
    assert "Catégorie supprimée avec succès." in response.content.decode()
    assert not EventCategory.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_category_delete_is_refused_when_linked(staff_client):
    category = EventCategory.objects.create(name="Occupée")
    Achievement.objects.create(title="Rattachée", category=category)

    response = staff_client.post(
        f"/espace/types-evenements/{category.pk}/supprimer/", {}, follow=True
    )
    assert "Impossible de supprimer" in response.content.decode()
    assert EventCategory.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_category_list_search_filters(staff_client):
    EventCategory.objects.create(name="Mariages")
    EventCategory.objects.create(name="Séminaires")

    response = staff_client.get("/espace/types-evenements/?q=Mari")
    assert response.status_code == 200
    assert list(response.context["categories"]) == list(
        EventCategory.objects.filter(name__icontains="Mari")
    )
    assert "Séminaires" not in response.content.decode()


@pytest.mark.django_db
def test_category_list_paginates(staff_client):
    for index in range(11):
        EventCategory.objects.create(name=f"Type {index:02d}")

    response = staff_client.get("/espace/types-evenements/")
    assert len(response.context["categories"]) == 10
    response = staff_client.get("/espace/types-evenements/?page=2")
    assert response.status_code == 200
    assert len(response.context["categories"]) == 1


# ---------------------------------------------------------------------------
# Réalisations
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_achievement_create_with_images(staff_client, media_root):
    category = EventCategory.objects.create(name="Galerie")
    data = {
        "title": "Mariage Aïcha",
        "category": str(category.pk),
        "is_active": "on",
        "images-0-image": make_image(name="a.jpg"),
        **image_formset(extra_images=3, initial=0),
    }
    response = staff_client.post("/espace/realisations/nouvelle/", data, follow=True)
    assert "Réalisation créée avec succès." in response.content.decode()
    achievement = Achievement.objects.get(title="Mariage Aïcha")
    assert achievement.category == category
    assert achievement.images.count() == 1


@pytest.mark.django_db
def test_achievement_create_requires_title(staff_client):
    category = EventCategory.objects.create(name="Galerie")
    data = {
        "title": "",
        "category": str(category.pk),
        **image_formset(extra_images=3, initial=0),
    }
    response = staff_client.post("/espace/realisations/nouvelle/", data)
    assert response.status_code == 200
    assert not Achievement.objects.exists()


@pytest.mark.django_db
def test_achievement_update_toggle_delete(staff_client, media_root):
    category = EventCategory.objects.create(name="Galerie")
    achievement = Achievement.objects.create(title="Avant", category=category)

    response = staff_client.post(
        f"/espace/realisations/{achievement.pk}/modifier/",
        {"title": "Après", "category": str(category.pk), "is_active": "on",
         **image_formset(extra_images=3, initial=0)},
        follow=True,
    )
    assert "Réalisation modifiée avec succès." in response.content.decode()
    achievement.refresh_from_db()
    assert achievement.title == "Après"

    response = staff_client.post(f"/espace/realisations/{achievement.pk}/basculer/", {}, follow=True)
    achievement.refresh_from_db()
    assert achievement.is_active is False
    assert "Réalisation désactivée avec succès." in response.content.decode()

    response = staff_client.post(
        f"/espace/realisations/{achievement.pk}/supprimer/", {}, follow=True
    )
    assert "Réalisation supprimée avec succès." in response.content.decode()
    assert not Achievement.objects.filter(pk=achievement.pk).exists()


@pytest.mark.django_db
def test_achievement_list_search_and_category_filter(staff_client):
    cat_a = EventCategory.objects.create(name="Mariages")
    cat_b = EventCategory.objects.create(name="Séminaires")
    Achievement.objects.create(title="Super fête", category=cat_a)
    Achievement.objects.create(title="Réunion", category=cat_b)

    response = staff_client.get("/espace/realisations/?q=Super")
    titles = [a.title for a in response.context["achievements"]]
    assert titles == ["Super fête"]

    response = staff_client.get(f"/espace/realisations/?categorie={cat_b.pk}")
    titles = [a.title for a in response.context["achievements"]]
    assert titles == ["Réunion"]


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_service_create_update_toggle_delete(staff_client, media_root):
    response = staff_client.post(
        "/espace/services/nouveau/",
        {
            "title": "Décoration",
            "description": "Salle et tables.",
            "cover_image": make_image(name="cover.jpg"),
            "is_active": "on",
        },
        follow=True,
    )
    assert "Service créé avec succès." in response.content.decode()
    service = Service.objects.get(title="Décoration")

    response = staff_client.post(
        f"/espace/services/{service.pk}/modifier/",
        {"title": "Décoration premium", "description": "Salle.", "is_active": "on"},
        follow=True,
    )
    assert "Service modifié avec succès." in response.content.decode()
    service.refresh_from_db()
    assert service.title == "Décoration premium"

    response = staff_client.post(f"/espace/services/{service.pk}/basculer/", {}, follow=True)
    service.refresh_from_db()
    assert service.is_active is False
    assert "Service désactivé avec succès." in response.content.decode()

    response = staff_client.post(f"/espace/services/{service.pk}/supprimer/", {}, follow=True)
    assert "Service supprimé avec succès." in response.content.decode()
    assert not Service.objects.filter(pk=service.pk).exists()


@pytest.mark.django_db
def test_service_list_search_filters(staff_client):
    Service.objects.create(title="Sonorisation")
    Service.objects.create(title="Traiteur")

    response = staff_client.get("/espace/services/?q=Son")
    assert "Traiteur" not in response.content.decode()
    assert "Sonorisation" in response.content.decode()


# ---------------------------------------------------------------------------
# Entreprise, paramètres, clients
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_company_form_creates_when_absent(staff_client):
    response = staff_client.post(
        "/espace/entreprise/",
        {
            "name": "KCDélices",
            "presentation": "Une équipe passionnée.",
            "mission": "",
            "vision": "",
            "location": "Douala",
            "phones": "+237 600 000 000\n+237 610 000 000",
            "whatsapp": "600000000",
            "email": "contact@kcdelice.cm",
            "social_links": "Facebook | https://facebook.com/kcdelice",
        },
        follow=True,
    )
    assert "mises à jour avec succès." in response.content.decode()
    company = Company.get_solo()
    assert company.name == "KCDélices"
    assert company.phones == ["+237 600 000 000", "+237 610 000 000"]
    assert company.social_links == [
        {"label": "Facebook", "url": "https://facebook.com/kcdelice"}
    ]


@pytest.mark.django_db
def test_company_form_updates_existing(staff_client):
    Company.objects.create(name="Avant", location="Yaoundé")
    response = staff_client.post(
        "/espace/entreprise/",
        {
            "name": "Après",
            "presentation": "",
            "mission": "",
            "vision": "",
            "location": "Douala",
            "phones": "",
            "whatsapp": "",
            "email": "",
            "social_links": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Company.get_solo().name == "Après"


@pytest.mark.django_db
def test_company_form_rejects_invalid_social_link(staff_client):
    response = staff_client.post(
        "/espace/entreprise/",
        {
            "name": "KC",
            "presentation": "",
            "mission": "",
            "vision": "",
            "location": "",
            "phones": "",
            "whatsapp": "",
            "email": "",
            "social_links": "Facebook sans url",
        },
    )
    assert response.status_code == 200
    assert not Company.objects.exists()


@pytest.mark.django_db
def test_settings_changes_password(staff_client, staff_user):
    response = staff_client.post(
        "/espace/parametres/",
        {
            "old_password": "Pass1234!",
            "new_password1": "NouveauMot99!",
            "new_password2": "NouveauMot99!",
        },
        follow=True,
    )
    assert "Mot de passe modifié avec succès." in response.content.decode()
    staff_user.refresh_from_db()
    assert staff_user.check_password("NouveauMot99!")


@pytest.mark.django_db
def test_settings_rejects_wrong_current_password(staff_client):
    response = staff_client.post(
        "/espace/parametres/",
        {
            "old_password": "faux",
            "new_password1": "NouveauMot99!",
            "new_password2": "NouveauMot99!",
        },
    )
    assert response.status_code == 200
    assert "correct" in response.content.decode()


@pytest.mark.django_db
def test_clients_page_is_placeholder(staff_client):
    response = staff_client.get("/espace/clients/")
    assert response.status_code == 200
    assert "prochainement" in response.content.decode()


@pytest.mark.django_db
def test_achievement_and_service_lists_support_ajax_filters(staff_client):
    category = EventCategory.objects.create(name="Galerie")
    Achievement.objects.create(title="Réalisation AJAX", category=category)
    Service.objects.create(title="Service AJAX")

    for url, marker in (
        ("/espace/realisations/", "Réalisation AJAX"),
        ("/espace/services/", "Service AJAX"),
    ):
        response = staff_client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.status_code == 200
        body = response.content.decode()
        assert "<html" not in body
        assert marker in body


@pytest.mark.django_db
def test_settings_page_has_live_password_validation(staff_client):
    response = staff_client.get("/espace/parametres/")
    body = response.content.decode()
    assert "data-password-form" in body
    assert "data-password-strength-bar" in body
    # Les consignes techniques de Django ne sont plus imprimées en bloc.
    assert "trop ressembler à vos autres informations" not in body
