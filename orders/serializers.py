from rest_framework import serializers
from django.db import transaction
from catalog.models import ProductVariant
from inventory.models import StockItem
from .models import Order, OrderItem
from inventory.services import InventoryService


class OrderItemCreateSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data["items"]

        with transaction.atomic():
            order = Order.objects.create(user=user)

            total = 0

            for item in items_data:
                variant = ProductVariant.objects.select_for_update().get(id=item["variant_id"])

                stock = StockItem.objects.select_for_update().get(variant=variant)
                available = stock.on_hand - stock.reserved

                if item["quantity"] > available:
                    raise serializers.ValidationError(
                        f"Not enough stock for {variant.sku}"
                    )

                order_item = OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=item["quantity"],

                    product_title=variant.product.title,
                    sku=variant.sku,
                    attributes_text=variant.attributes_text,

                    unit_price_amount=variant.price_amount,
                    unit_discount_amount=0,
                )

                total += order_item.total_amount

                InventoryService.reserve(
                    variant=variant,
                    qty=item["quantity"],
                    note=f"Order {order.id} created"
                )

            order.total_amount = total
            order.save(update_fields=["total_amount"])

        return order


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_title",
            "sku",
            "attributes_text",
            "unit_price_amount",
            "unit_discount_amount",
            "quantity",
            "total_amount",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_amount",
            "created_at",
            "items",
        )