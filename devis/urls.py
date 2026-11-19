from django.urls import path

from .views import (
    QuoteCreateView,
    QuoteDetailView,
    QuoteItemCreateView,
    QuoteItemDeleteView,
    QuoteListView,
)

urlpatterns = [
    path("", QuoteListView.as_view(), name="quote_list"),
    path("nouveau/", QuoteCreateView.as_view(), name="quote_create"),
    path("<uuid:pk>/", QuoteDetailView.as_view(), name="quote_detail"),
    path("<uuid:pk>/ligne/", QuoteItemCreateView.as_view(), name="quote_item_add"),
    path(
        "ligne/<uuid:pk>/supprimer/",
        QuoteItemDeleteView.as_view(),
        name="quote_item_delete",
    ),
]
