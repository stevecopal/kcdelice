from django.urls import path

from .views import (
    AboutView,
    AchievementCreateView,
    AchievementDeleteView,
    AchievementListView,
    AchievementToggleView,
    AchievementUpdateView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryToggleView,
    CategoryUpdateView,
    CategoryDetailView,
    ClientsView,
    CompanyUpdateView,
    DashboardView,
    HomeView,
    LoginView,
    LogoutView,
    ServiceCreateView,
    ServiceDeleteView,
    ServiceListView,
    ServiceToggleView,
    ServiceUpdateView,
    ServicesView,
    SettingsView,
)
from .views.pwa import icon as pwa_icon
from .views.pwa import manifest as pwa_manifest
from .views.pwa import offline as pwa_offline
from .views.pwa import service_worker as pwa_service_worker

urlpatterns = [
    # Espace public
    path("", HomeView.as_view(), name="home"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path("services/", ServicesView.as_view(), name="services"),
    path("a-propos/", AboutView.as_view(), name="about"),
    # Authentification
    path("connexion/", LoginView.as_view(), name="login"),
    path("deconnexion/", LogoutView.as_view(), name="logout"),
    # Administration
    path("espace/", DashboardView.as_view(), name="dashboard"),
    # Application installable (PWA) de l'espace d'administration
    path("espace/manifeste.webmanifest", pwa_manifest, name="espace_manifest"),
    path("espace/icone-<int:size>.png", pwa_icon, name="espace_icon"),
    path("espace/service-worker.js", pwa_service_worker, name="espace_service_worker"),
    path("espace/hors-ligne/", pwa_offline, name="espace_offline"),
    path("espace/clients/", ClientsView.as_view(), name="clients"),
    path("espace/parametres/", SettingsView.as_view(), name="settings"),
    path("espace/entreprise/", CompanyUpdateView.as_view(), name="company_update"),
    # Types d'événements
    path("espace/types-evenements/", CategoryListView.as_view(), name="category_list"),
    path(
        "espace/types-evenements/nouveau/",
        CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "espace/types-evenements/<uuid:pk>/modifier/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "espace/types-evenements/<uuid:pk>/supprimer/",
        CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path(
        "espace/types-evenements/<uuid:pk>/basculer/",
        CategoryToggleView.as_view(),
        name="category_toggle",
    ),
    # Réalisations
    path("espace/realisations/", AchievementListView.as_view(), name="achievement_list"),
    path(
        "espace/realisations/nouvelle/",
        AchievementCreateView.as_view(),
        name="achievement_create",
    ),
    path(
        "espace/realisations/<uuid:pk>/modifier/",
        AchievementUpdateView.as_view(),
        name="achievement_update",
    ),
    path(
        "espace/realisations/<uuid:pk>/supprimer/",
        AchievementDeleteView.as_view(),
        name="achievement_delete",
    ),
    path(
        "espace/realisations/<uuid:pk>/basculer/",
        AchievementToggleView.as_view(),
        name="achievement_toggle",
    ),
    # Services
    path("espace/services/", ServiceListView.as_view(), name="service_list"),
    path("espace/services/nouveau/", ServiceCreateView.as_view(), name="service_create"),
    path(
        "espace/services/<uuid:pk>/modifier/",
        ServiceUpdateView.as_view(),
        name="service_update",
    ),
    path(
        "espace/services/<uuid:pk>/supprimer/",
        ServiceDeleteView.as_view(),
        name="service_delete",
    ),
    path(
        "espace/services/<uuid:pk>/basculer/",
        ServiceToggleView.as_view(),
        name="service_toggle",
    ),
]
