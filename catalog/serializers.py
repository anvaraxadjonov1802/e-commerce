from rest_framework import serializers
from .models import ProductVariant, Product, ProductImage, Category


class ProductVariantSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "attributes_text",
            "price_amount",
            "is_active",
            'available',
        )


    def get_available(self, obj):
        if hasattr(obj, "stock") and obj.stock:
            return obj.stock.on_hand - obj.stock.reserved
        return 0


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "id",
            "image",
            "is_main",
        )


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "images",
            "description",
            "category",
            "variants",
            "created_at",

        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug"
        )
