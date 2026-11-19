from django.contrib import admin

from .models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ("title", "quantity", "unit_price", "total_price")
    readonly_fields = ("total_price",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "client_name",
        "client_phone",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("reference", "client_name", "client_phone", "event_location")
    readonly_fields = ("reference", "subtotal", "total_amount", "created_at", "updated_at")
    inlines = (QuoteItemInline,)


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ("title", "quote", "quantity", "unit_price", "total_price")
    search_fields = ("title", "quote__reference", "quote__client_name")
    list_select_related = ("quote",)
