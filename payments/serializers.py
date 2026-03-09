import uuid
from rest_framework import serializers
from django.conf import settings
from orders.models import Order
from .models import Payment


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


class ManualPaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)

    def create(self, validated_data):
        user = self.context["request"].user
        order = Order.objects.get(id=validated_data["order_id"], user=user)

        if order.status != Order.Status.PENDING:
            raise serializers.ValidationError("Order is not payable")

        # orderga method yozib qo‘yamiz
        order.payment_method = validated_data["method"]
        order.save(update_fields=["payment_method"])

        payment = Payment.objects.create(
            order=order,
            provider="manual",
            transaction_id=str(uuid.uuid4()),
            amount=order.total_amount,
            method=validated_data["method"],
            status=Payment.Status.PENDING
        )
        return payment

    def to_representation(self, instance):
        data = {
            "payment_id": str(instance.id),
            "order_id": str(instance.order_id),
            "amount": instance.amount,
            "status": instance.status,
            "method": instance.method,
        }

        # karta rekvizitlari
        if instance.method == Payment.PaymentMethod.CARD_TRANSFER:
            data["card"] = {
                "owner": getattr(settings, "CARD_OWNER", ""),
                "number": getattr(settings, "CARD_NUMBER", ""),
                "bank": getattr(settings, "CARD_BANK", ""),
            }
        else:
            data["instructions"] = "Cash payment on delivery"

        return data


class AdminPaymentConfirmSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    success = serializers.BooleanField(default=True)
    note = serializers.CharField(required=False, allow_blank=True)