"""Application installable de l'espace d'administration (PWA)."""

import json
from io import BytesIO

import pytest
from PIL import Image

from core.models import Company


@pytest.mark.django_db
def test_manifest_targets_admin_and_uses_company_name(client):
    Company.objects.create(name="Délices & Co")

    response = client.get("/espace/manifeste.webmanifest")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/manifest+json"
    data = json.loads(response.content)
    assert data["start_url"] == "/espace/"
    assert data["scope"] == "/"
    assert data["display"] == "standalone"
    assert "Délices & Co" in data["name"]
    sizes = {icon["sizes"] for icon in data["icons"]}
    assert {"192x192", "512x512"} <= sizes


@pytest.mark.django_db
def test_icons_are_square_png(client):
    Company.objects.create(name="Délices")

    for size in (192, 512):
        response = client.get(f"/espace/icone-{size}.png")
        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        image = Image.open(BytesIO(response.content))
        assert image.size == (size, size)

    assert client.get("/espace/icone-64.png").status_code == 404


@pytest.mark.django_db
def test_service_worker_is_served_for_site_scope(client):
    response = client.get("/espace/service-worker.js")

    assert response.status_code == 200
    assert "javascript" in response["Content-Type"]
    assert response["Service-Worker-Allowed"] == "/"
    body = response.content.decode()
    assert "addEventListener(\"fetch\"" in body
    assert "/espace/hors-ligne/" in body


@pytest.mark.django_db
def test_login_page_links_manifest_and_install_button(client):
    response = client.get("/connexion/")
    body = response.content.decode()

    assert response.status_code == 200
    assert "/espace/manifeste.webmanifest" in body
    assert "data-pwa-install" in body
    assert "js/pwa.js" in body


@pytest.mark.django_db
def test_offline_page_is_public(client):
    response = client.get("/espace/hors-ligne/")

    assert response.status_code == 200
    assert "Réessayer" in response.content.decode()
