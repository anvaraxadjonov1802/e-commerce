from rest_framework import generics, permissions
from .serializers import OrderCreateSerializer, OrderSerializer
from .models import Order


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .services import OrderService

class OrderMarkPaidView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        OrderService.mark_as_paid(order)
        return Response({"status": "paid"})