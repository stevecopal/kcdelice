from django.contrib import admin

from .forms import CompanyForm
from .models import Achievement, AchievementImage, Company, EventCategory, Service


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyForm
    fieldsets = (
        ("Identité", {"fields": ("name", "logo")}),
        ("Présentation", {"fields": ("presentation", "mission", "vision")}),
        ("Contact", {"fields": ("location", "phones", "whatsapp", "email")}),
    )

    def has_add_permission(self, request):
        return not Company.objects.exists()


class AchievementImageInline(admin.TabularInline):
    model = AchievementImage
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("image", "created_at")


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "updated_at")
    list_filter = ("is_active", "category")
    search_fields = ("title",)
    list_select_related = ("category",)
    inlines = (AchievementImageInline,)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
