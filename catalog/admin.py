from django.contrib import admin

from catalog.models import Product, Category, ProductVariant, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', "slug", "created_at")
    search_fields = ('name', "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active","created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "sku", "attributes_text", "price_amount", "is_active", "created_at")
    list_filter = ("is_active", "product")
    search_fields = ("sku", "attributes_text", "product__title")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "created_at")
    list_filter = ("is_main", )
    