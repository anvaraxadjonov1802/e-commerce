from rest_framework import serializers
from orders.models import Order
from .models import Payment
import uuid


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    provider = serializers.CharField()

    def create(self, validated_data):
        order = Order.objects.get(id=validated_data["order_id"])

        if order.status != Order.Status.PENDING:
            raise serializers.ValidationError("Order not payable")

        payment = Payment.objects.create(
            order=order,
            provider=validated_data["provider"],
            transaction_id=str(uuid.uuid4()),  # fake for now
            amount=order.total_amount
        )

        return payment