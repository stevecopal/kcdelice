from django.urls import path

from .views import AboutView, CategoryDetailView, HomeView, ServicesView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path("services/", ServicesView.as_view(), name="services"),
    path("a-propos/", AboutView.as_view(), name="about"),
]
