from django.urls import path

from .views import (
    QuoteDeleteView,
    QuoteDetailView,
    QuoteFormView,
    QuoteItemCreateView,
    QuoteItemDeleteView,
    QuoteListView,
    QuotePDFView,
    QuoteStatusUpdateView,
)

urlpatterns = [
    path("", QuoteListView.as_view(), name="quote_list"),
    path("nouveau/", QuoteFormView.as_view(), name="quote_create"),
    path("<uuid:pk>/", QuoteDetailView.as_view(), name="quote_detail"),
    path("<uuid:pk>/modifier/", QuoteFormView.as_view(), name="quote_update"),
    path("<uuid:pk>/statut/", QuoteStatusUpdateView.as_view(), name="quote_status"),
    path("<uuid:pk>/pdf/", QuotePDFView.as_view(), name="quote_pdf"),
    path("<uuid:pk>/supprimer/", QuoteDeleteView.as_view(), name="quote_delete"),
    path("<uuid:pk>/ligne/", QuoteItemCreateView.as_view(), name="quote_item_add"),
    path(
        "ligne/<uuid:pk>/supprimer/",
        QuoteItemDeleteView.as_view(),
        name="quote_item_delete",
    ),
]
