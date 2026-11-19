from django.contrib import admin

from .models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ("label", "quantity", "unit_price")
    readonly_fields = ()


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("title", "client_name", "total_display", "updated_at")
    search_fields = ("title", "client_name", "client_email")
    list_select_related = ()
    inlines = (QuoteItemInline,)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Total")
    def total_display(self, obj) -> str:
        return f"{obj.total} FCFA"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("items")


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ("label", "quote", "quantity", "unit_price")
    search_fields = ("label", "quote__title")
    list_select_related = ("quote",)
