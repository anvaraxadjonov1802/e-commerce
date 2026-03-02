from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_title", "sku", "attributes_text", "unit_price_amount", "total_amount", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__phone", "user__full_name")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "sku", "quantity", "unit_price_amount", "total_amount", "created_at")
    search_fields = ("sku", "product_title")
    readonly_fields = ("created_at",)
