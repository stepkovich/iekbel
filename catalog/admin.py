from django.contrib import admin
from .models import Distributor, Location, DdpNode, Product


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


@admin.register(DdpNode)
class DdpNodeAdmin(admin.ModelAdmin):
    list_display = ("ddp_id", "title", "level", "products_count")
    search_fields = ("ddp_id", "title")
    list_filter = ("level",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "price", "rrc", "stock_total", "ddp")
    search_fields = ("sku", "name")
    list_filter = ("tm", "is_active")
    ordering = ("sku",)
