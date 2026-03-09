from rest_framework import generics, permissions, status
from .serializers import PaymentCreateSerializer, ManualPaymentCreateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db import transaction

from .models import Payment
from orders.models import Order
from orders.services import OrderService
from .serializers import AdminPaymentConfirmSerializer


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManualPaymentCreateView(generics.CreateAPIView):
    serializer_class = ManualPaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentWebhookView(APIView):
    permission_classes = []  # provider auth key bilan himoyalanadi keyin

    @transaction.atomic
    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        status_from_provider = request.data.get("status")

        try:
            payment = Payment.objects.select_for_update().get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found"}, status=404)

        # IDEMPOTENT CHECK
        if payment.status == Payment.Status.SUCCESS:
            return Response({"detail": "Already processed"})

        if status_from_provider == "success":
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["status"])

            # 🔥 ORDER PAID
            OrderService.mark_as_paid(payment.order)

        elif status_from_provider == "failed":
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])

        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


class AdminPaymentConfirmView(APIView):
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request):
        s = AdminPaymentConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        payment = Payment.objects.select_for_update().get(id=s.validated_data["payment_id"])

        # idempotent
        if payment.status == Payment.Status.SUCCESS:
            return Response({"detail": "already confirmed"})

        if s.validated_data["success"] is True:
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["status"])

            OrderService.mark_as_paid(payment.order)

            return Response({"detail": "confirmed", "order_status": payment.order.status})

        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])

        # fail bo‘lsa order cancel qilmaymiz (xohlasang qilamiz)
        return Response({"detail": "marked failed"})