from .achievements import (
    AchievementCreateView,
    AchievementDeleteView,
    AchievementListView,
    AchievementToggleView,
    AchievementUpdateView,
    CategoryDetailView,
)
from .authentication import LoginView, LogoutView
from .company import AboutView, CompanyUpdateView
from .dashboard import DashboardView
from .events import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryToggleView,
    CategoryUpdateView,
)
from .misc import ClientsView, SettingsView
from .public import HomeView
from .services import (
    ServiceCreateView,
    ServiceDeleteView,
    ServiceListView,
    ServiceToggleView,
    ServiceUpdateView,
    ServicesView,
)

__all__ = [
    "AboutView",
    "AchievementCreateView",
    "AchievementDeleteView",
    "AchievementListView",
    "AchievementToggleView",
    "AchievementUpdateView",
    "CategoryCreateView",
    "CategoryDeleteView",
    "CategoryDetailView",
    "CategoryListView",
    "CategoryToggleView",
    "CategoryUpdateView",
    "ClientsView",
    "CompanyUpdateView",
    "DashboardView",
    "HomeView",
    "LoginView",
    "LogoutView",
    "ServiceCreateView",
    "ServiceDeleteView",
    "ServiceListView",
    "ServiceToggleView",
    "ServiceUpdateView",
    "ServicesView",
    "SettingsView",
]
