from django.contrib import admin
from .models import Distributor, Location


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("name", "iek_status", "site", "updated")
    list_filter = ("iek_status",)
    search_fields = ("name", "legal_name")
    inlines = [LocationInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "address", "type", "distributor", "phone")
    list_filter = ("type",)
    search_fields = ("city", "address", "distributor__name")
