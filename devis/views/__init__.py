from .detail import QuoteDeleteView, QuoteDetailView, QuoteStatusUpdateView
from .form import QuoteFormView
from .items import QuoteItemCreateView, QuoteItemDeleteView
from .list import QuoteListView
from .pdf import QuotePDFView

__all__ = [
    "QuoteDeleteView",
    "QuoteDetailView",
    "QuoteFormView",
    "QuoteItemCreateView",
    "QuoteItemDeleteView",
    "QuoteListView",
    "QuotePDFView",
    "QuoteStatusUpdateView",
]
