"""Tests de l'administration minimale (Django admin) : accès, CRUD, uploads."""

import pytest

from core.forms import CompanyForm
from core.models import Achievement, Company, EventCategory, Service

from .factories import make_image


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(username="admin", password="pass")


@pytest.fixture
def auth_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


@pytest.mark.django_db
def test_admin_requires_login(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_admin_category_create_change_delete(auth_client):
    response = auth_client.post(
        "/admin/core/eventcategory/add/",
        {"name": "Soirees", "is_active": "on"},
    )
    assert response.status_code == 302
    category = EventCategory.objects.get(name="Soirees")

    response = auth_client.post(
        f"/admin/core/eventcategory/{category.pk}/change/",
        {"name": "Soirees pro", "is_active": "on"},
    )
    assert response.status_code == 302
    category.refresh_from_db()
    assert category.name == "Soirees pro"

    response = auth_client.post(
        f"/admin/core/eventcategory/{category.pk}/delete/",
        {"post": "yes"},
    )
    assert response.status_code == 302
    assert not EventCategory.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_admin_delete_category_with_achievements_is_refused(auth_client):
    category = EventCategory.objects.create(name="Occupee")
    Achievement.objects.create(title="Realisation", category=category)
    response = auth_client.post(
        f"/admin/core/eventcategory/{category.pk}/delete/",
        {"post": "yes"},
    )
    assert response.status_code == 200
    assert EventCategory.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_admin_create_achievement_with_category(auth_client):
    category = EventCategory.objects.create(name="Galerie")
    response = auth_client.post(
        "/admin/core/achievement/add/",
        {
            "title": "Realisation 1",
            "category": str(category.pk),
            "is_active": "on",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )
    assert response.status_code == 302
    achievement = Achievement.objects.get(title="Realisation 1")
    assert achievement.category == category


@pytest.mark.django_db
def test_admin_add_images_to_achievement(auth_client, media_root):
    category = EventCategory.objects.create(name="Galerie")
    response = auth_client.post(
        "/admin/core/achievement/add/",
        {
            "title": "Photo",
            "category": str(category.pk),
            "is_active": "on",
            "images-TOTAL_FORMS": "2",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "images-0-image": make_image(name="a.jpg"),
            "images-1-image": make_image(name="b.jpg"),
        },
    )
    assert response.status_code == 302
    achievement = Achievement.objects.get(title="Photo")
    assert achievement.images.count() == 2


@pytest.mark.django_db
def test_admin_create_service_with_cover_image(auth_client, media_root):
    response = auth_client.post(
        "/admin/core/service/add/",
        {
            "title": "Decoration",
            "cover_image": make_image(name="cover.jpg"),
            "description": "Salle et table.",
            "is_active": "on",
        },
    )
    assert response.status_code == 302
    service = Service.objects.get(title="Decoration")
    assert service.cover_image.name.startswith("services/")


@pytest.mark.django_db
def test_admin_company_cannot_be_added_twice(auth_client):
    company = Company.objects.create(name="KCDelices")
    response = auth_client.get("/admin/core/company/add/")
    assert response.status_code == 403

    response = auth_client.post(
        f"/admin/core/company/{company.pk}/change/",
        {
            "name": "KCDelices",
            "presentation": "",
            "mission": "",
            "vision": "",
            "location": "Douala",
            "phones": "+237 600 000 000\n+237 611 111 111",
            "whatsapp": "600000000",
            "email": "contact@kc.example",
        },
    )
    assert response.status_code == 302
    company.refresh_from_db()
    assert company.phones == ["+237 600 000 000", "+237 611 111 111"]
    assert company.location == "Douala"


@pytest.mark.django_db
def test_company_form_parses_phones_from_textarea():
    form = CompanyForm(
        data={
            "name": "KC",
            "presentation": "",
            "mission": "",
            "vision": "",
            "location": "",
            "phones": "+237 600\n\n+237 610\n",
            "whatsapp": "",
            "email": "",
        }
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["phones"] == ["+237 600", "+237 610"]
