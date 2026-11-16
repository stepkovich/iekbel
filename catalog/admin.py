from django.contrib import admin

admin.site.site_header = "иэк.бел — админка представительства"
admin.site.site_title = "иэк.бел"
admin.site.index_title = "Каталог, дистрибьюторы, заказы"

from django.contrib import admin
from .models import Distributor, Location, DdpNode, Product, Order


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "created", "distributor", "client_name",
                    "client_phone", "status", "items_count")
    list_filter = ("status", "client_type")
    search_fields = ("order_id", "client_name", "client_phone", "client_email",
                     "client_org", "distributor")
    list_editable = ("status",)
    date_hierarchy = "created"
    readonly_fields = ("order_id", "created", "distributor", "client_name",
                       "client_phone", "client_email", "client_type", "client_org",
                       "client_requisites", "client_city", "comment", "items")
    fieldsets = [
        ("Заявка", {"fields": ["order_id", "created", "status", "distributor"]}),
        ("Клиент", {"fields": ["client_name", "client_phone", "client_email",
                               "client_type", "client_org", "client_city",
                               "client_requisites", "comment"]}),
        ("Позиции", {"fields": ["items"]}),
        ("Работа менеджера", {"fields": ["note"]}),
    ]

    @admin.display(description="Позиций")
    def items_count(self, obj):
        return len(obj.items or [])

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # позиции показываем отформатированным текстом, а не JSON-строкой
        obj = self.get_object(request, object_id)
        if obj:
            lines = [f"{i + 1}. {it.get('title', '')} ({it.get('sku', '')}) — {it.get('qty', '')} шт"
                     for i, it in enumerate(obj.items or [])]
            obj.items = "\n".join(lines) or "—"
        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        css = {"all": ("catalog/order_items.css",)}
