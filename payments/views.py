from rest_framework import generics, permissions, status
from .serializers import PaymentCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Payment
from orders.services import OrderService


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
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