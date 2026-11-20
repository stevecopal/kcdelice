"""Suivi léger de l'activité publique et indicateurs du tableau de bord."""

import pytest

from core.models import Achievement, EventCategory, PageView, Service, User
from devis.models import Quote


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username="staff", password="Pass1234!", is_staff=True)


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user)
    return client


@pytest.mark.django_db
def test_public_visits_are_recorded(client):
    client.get("/")
    client.get("/a-propos/")

    assert PageView.objects.filter(kind=PageView.Kind.SITE).count() == 2
    assert PageView.objects.filter(kind=PageView.Kind.SITE, path="/").exists()


@pytest.mark.django_db
def test_category_page_records_category_and_achievement_views(client):
    category = EventCategory.objects.create(name="Mariages")
    achievement = Achievement.objects.create(title="Mariage A", category=category)
    Achievement.objects.create(title="Mariage B", category=category)

    client.get(f"/categories/{category.pk}/")

    assert PageView.objects.filter(
        kind=PageView.Kind.CATEGORY, target_id=category.pk
    ).count() == 1
    assert PageView.objects.filter(
        kind=PageView.Kind.ACHIEVEMENT, target_id=achievement.pk
    ).count() == 1
    assert PageView.objects.filter(kind=PageView.Kind.ACHIEVEMENT).count() == 2


@pytest.mark.django_db
def test_services_page_records_service_views(client):
    service = Service.objects.create(title="Traiteur")
    Service.objects.create(title="Décoration", is_active=False)

    client.get("/services/")

    assert PageView.objects.filter(
        kind=PageView.Kind.SERVICE, target_id=service.pk
    ).count() == 1
    # Un service inactif n'est pas affiché, donc pas compté.
    assert PageView.objects.filter(kind=PageView.Kind.SERVICE).count() == 1


@pytest.mark.django_db
def test_staff_browsing_is_not_counted(staff_client):
    staff_client.get("/")
    staff_client.get("/services/")

    assert PageView.objects.count() == 0


@pytest.mark.django_db
def test_dashboard_aggregates_real_data(staff_client, staff_user):
    category = EventCategory.objects.create(name="Mariages")
    top = Achievement.objects.create(title="Très vue", category=category)
    Achievement.objects.create(title="Moins vue", category=category)
    service = Service.objects.create(title="Traiteur")
    Quote.objects.create(
        client_name="Aïcha", client_phone="+237 600", event_location="Douala"
    )

    PageView.objects.create(kind=PageView.Kind.SITE, path="/")
    PageView.objects.create(kind=PageView.Kind.SITE, path="/a-propos/")
    PageView.objects.create(kind=PageView.Kind.CATEGORY, target_id=category.pk)
    for _ in range(3):
        PageView.objects.create(kind=PageView.Kind.ACHIEVEMENT, target_id=top.pk)
    PageView.objects.create(kind=PageView.Kind.ACHIEVEMENT, target_id=top.pk)
    PageView.objects.create(kind=PageView.Kind.SERVICE, target_id=service.pk)

    response = staff_client.get("/espace/")
    assert response.status_code == 200

    stats = {stat["label"]: stat["value"] for stat in response.context["stats"]}
    assert stats["Devis"] == 1
    assert stats["Réalisations"] == 2

    public = response.context["public_stats"]
    assert public["visits"] == 2
    assert public["categories"] == 1
    assert public["achievements"] == 4
    assert public["services"] == 1

    assert response.context["top_achievements"][0]["object"] == top
    assert response.context["top_services"][0]["object"] == service
