from django.contrib import admin
from django.utils.html import format_html

admin.site.site_header = "иэк.бел — админка представительства"
admin.site.site_title = "иэк.бел"
admin.site.index_title = "Каталог, дистрибьюторы, заказы"

from django.contrib import admin
from django.utils.html import format_html
from .models import Distributor, Location, DdpNode, Product, Order, News


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "updated")
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


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("date", "kind_badge", "title", "is_published", "photo_preview")
    list_filter = ("kind", "is_published", "date")
    search_fields = ("title", "announcement", "body")
    prepopulated_fields = {"slug": ("title",)}
    list_per_page = 25
    fieldsets = [
        (None, {"fields": ["title", "slug", "kind", "date", "is_published"]}),
        ("Контент", {"fields": ["announcement", "body"]}),
        ("Фото", {"fields": ["photo", "photo_caption"]}),
    ]

    @admin.display(description="Рубрика")
    def kind_badge(self, obj):
        colors = {"news": "#F6E200", "event": "#FFDF00", "company": "#EDEEF1"}
        labels = {"news": "новость", "event": "мероприятие", "company": "о нас"}
        return format_html('<span style="background:{};padding:3px 9px;font-weight:700">{}</span>',
                           colors.get(obj.kind, "#EDEEF1"), labels.get(obj.kind, obj.kind))

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height:52px">', obj.photo.url)
        return "—"
