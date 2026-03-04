from django.contrib import admin
from .models import StockItem, StockMovement


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("variant", "on_hand", "reserved", "updated_at")
    search_fields = ("variant__sku", "variant__product__title")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("stock_item", "type", "quantity", "created_at")
    list_filter = ("type", "created_at")