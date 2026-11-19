"""Tests des modèles core : singleton, relations, validation des images."""

import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from PIL import Image

from core.models import Achievement, AchievementImage, Company, EventCategory, Service
from core.services.image import MAX_IMAGE_SIZE, optimize_image

from .factories import make_image


@pytest.mark.django_db
def test_company_is_singleton():
    assert Company.get_solo() is None
    company = Company.objects.create(name="KCDélices")
    assert Company.get_solo() == company
    with pytest.raises(ValidationError):
        Company.objects.create(name="Autre entreprise")


@pytest.mark.django_db
def test_company_clean_refuses_second_instance():
    Company.objects.create(name="KCDélices")
    with pytest.raises(ValidationError):
        Company(name="Doublon").clean()


@pytest.mark.django_db
def test_company_phone_list():
    company = Company(name="KC", phones=["+237 600 000 000", "", "+237 611 111 111"])
    assert company.phone_list == ["+237 600 000 000", "+237 611 111 111"]
    assert str(company) == "KC"


@pytest.mark.django_db
def test_event_category_str_and_default_active():
    category = EventCategory.objects.create(name="Mariages")
    assert str(category) == "Mariages"
    assert category.is_active is True


@pytest.mark.django_db
def test_achievement_belongs_to_category():
    category = EventCategory.objects.create(name="Anniversaires")
    achievement = Achievement.objects.create(title="Anniv. Jean", category=category)
    assert achievement.category == category
    assert str(achievement) == "Anniv. Jean"
    assert list(category.achievements.all()) == [achievement]


@pytest.mark.django_db
def test_deleting_category_with_achievements_is_protected():
    category = EventCategory.objects.create(name="Baptêmes")
    Achievement.objects.create(title="Bap. Léa", category=category)
    with pytest.raises(ProtectedError):
        category.delete()
    assert EventCategory.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_deleting_achievement_removes_its_images():
    category = EventCategory.objects.create(name="Baptêmes")
    achievement = Achievement.objects.create(title="Bap. Léa", category=category)
    image = AchievementImage.objects.create(achievement=achievement, image=make_image())
    achievement.delete()
    assert not AchievementImage.objects.filter(pk=image.pk).exists()


@pytest.mark.django_db
def test_achievement_main_image_property():
    category = EventCategory.objects.create(name="Soirées")
    achievement = Achievement.objects.create(title="Soirée A", category=category)
    assert achievement.main_image is None
    image = AchievementImage.objects.create(achievement=achievement, image=make_image())
    achievement.refresh_from_db()
    assert achievement.main_image.pk == image.pk


@pytest.mark.django_db
def test_service_str_and_default_active():
    service = Service.objects.create(title="Traiteur")
    assert str(service) == "Traiteur"
    assert service.is_active is True


@pytest.mark.django_db
def test_image_too_large_is_rejected():
    big = SimpleUploadedFile("big.jpg", b"x" * (MAX_IMAGE_SIZE + 1), "image/jpeg")
    category = EventCategory(name="Test", cover_image=big)
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_non_image_file_is_rejected():
    fake = SimpleUploadedFile("fake.jpg", b"ce n'est pas une image", "image/jpeg")
    category = EventCategory(name="Test", cover_image=fake)
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_valid_image_passes_clean():
    category = EventCategory(name="Test", cover_image=make_image())
    category.full_clean()  # ne doit pas lever d'erreur


def test_optimize_image_resizes_large_picture():
    large = make_image(name="large.jpg", size=(2400, 1200))
    result = optimize_image(large)
    result.seek(0)
    img = Image.open(io.BytesIO(result.read()))
    assert img.width == 1600


def test_optimize_image_keeps_small_picture_untouched():
    small = make_image(name="small.jpg", size=(100, 80))
    assert optimize_image(small) is small
