"""Tests des pages publiques : accueil, catégories, services, à propos, 404."""

import pytest
from django.template.loader import render_to_string
from django.urls import reverse

from core.models import Achievement, AchievementImage, Company, EventCategory, Service

from .factories import make_image


@pytest.mark.django_db
def test_home_shows_only_active_categories(client):
    EventCategory.objects.create(name="Anniversaires")
    EventCategory.objects.create(name="Masquee", is_active=False)
    response = client.get("/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Anniversaires" in content
    assert "Masquee" not in content


@pytest.mark.django_db
def test_home_paginates_categories(client):
    for index in range(13):
        EventCategory.objects.create(name=f"Cat {index:02d}")
    response = client.get("/")
    assert len(response.context["categories"]) == 12
    response = client.get("/?page=2")
    assert len(response.context["categories"]) == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_invalid_page_returns_404(client):
    EventCategory.objects.create(name="Seule")
    response = client.get("/?page=99")
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_empty_state(client):
    response = client.get("/")
    assert "Aucune réalisation" in response.content.decode()


@pytest.mark.django_db
def test_home_displays_company_name_from_context_processor(client):
    Company.objects.create(name="KCDélices Events")
    response = client.get("/")
    assert "KCDélices Events" in response.content.decode()


@pytest.mark.django_db
def test_category_page_lists_active_achievements_only(client):
    category = EventCategory.objects.create(name="Baptemes")
    active = Achievement.objects.create(title="Bapteme Actif", category=category)
    Achievement.objects.create(title="Bapteme Inactif", category=category, is_active=False)
    AchievementImage.objects.create(achievement=active, image=make_image())
    response = client.get(reverse("category_detail", args=[category.pk]))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Bapteme Actif" in content
    assert "Bapteme Inactif" not in content
    gallery = response.context["gallery_data"]
    assert len(gallery) == 1
    assert gallery[0]["id"] == str(active.id)
    assert len(gallery[0]["images"]) == 1


@pytest.mark.django_db
def test_category_page_shows_empty_state_without_achievements(client):
    category = EventCategory.objects.create(name="Vide")
    response = client.get(reverse("category_detail", args=[category.pk]))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Aucune réalisation" in content
    assert "Cette catégorie est actuellement vide." in content


@pytest.mark.django_db
def test_inactive_category_returns_404(client):
    category = EventCategory.objects.create(name="Masquee", is_active=False)
    response = client.get(reverse("category_detail", args=[category.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_category_returns_404(client):
    import uuid

    response = client.get(reverse("category_detail", args=[uuid.uuid4()]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_services_page_shows_only_active_services(client):
    Service.objects.create(title="Service Actif")
    Service.objects.create(title="Service Inactif", is_active=False)
    response = client.get("/services/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Service Actif" in content
    assert "Service Inactif" not in content


@pytest.mark.django_db
def test_services_page_paginates(client):
    for index in range(10):
        Service.objects.create(title=f"Service {index:02d}")
    response = client.get("/services/")
    assert len(response.context["services"]) == 9
    response = client.get("/services/?page=2")
    assert len(response.context["services"]) == 1


@pytest.mark.django_db
def test_about_page_uses_company_content_over_default(client):
    Company.objects.create(
        name="KC",
        presentation="Bienvenue chez nous.\n\nDeuxième paragraphe.",
        mission="",
        vision="Voir loin.",
    )
    response = client.get("/a-propos/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Bienvenue chez nous." in content
    assert "Deuxième paragraphe." in content
    assert "Voir loin." in content
    # Présentation, vision, mission et demande de devis.
    assert content.count("<h2") == 4
    assert "Notre mission est de transformer" in content


@pytest.mark.django_db
def test_about_page_without_company_uses_default_content(client):
    response = client.get("/a-propos/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Depuis 2015, KCDélices imagine" in content
    assert "Notre mission est de transformer" in content
    assert "Devenir la référence" in content
    # Aucune coordonnée : les sections éditoriales et le formulaire de devis.
    assert content.count("<h2") == 4


@pytest.mark.django_db
def test_about_page_contact_section_lists_phones(client):
    Company.objects.create(name="KC", location="Douala", phones=["+237 600", "+237 610"])
    response = client.get("/a-propos/")
    content = response.content.decode()
    assert "+237 600" in content
    assert "+237 610" in content
    assert "Douala" in content


@pytest.mark.django_db
def test_about_page_quote_form_targets_company_whatsapp(client):
    Company.objects.create(name="KC", whatsapp="+237 699 00 00 00")
    content = client.get("/a-propos/").content.decode()

    for field in ('name="name"', 'name="phone"', 'name="event"', 'name="place"', 'name="description"'):
        assert field in content
    # Le numéro est normalisé pour les liens wa.me.
    assert 'data-wa-number="237699000000"' in content
    assert "https://wa.me/237699000000" in content


@pytest.mark.django_db
def test_services_and_realisations_expose_whatsapp_button(client):
    Company.objects.create(name="KC", whatsapp="+237 699 00 00 00")
    for url in ("/", "/services/"):
        content = client.get(url).content.decode()
        assert "https://wa.me/237699000000" in content


def test_error_templates_render():
    for template_name in ("403.html", "404.html", "500.html"):
        html = render_to_string(template_name, {})
        assert "KCD" in html or "Retour à l'accueil" in html
