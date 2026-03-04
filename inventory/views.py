from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from catalog.models import ProductVariant
from .serializers import StockAdjustSerializer
from .services import InventoryService


class StockIncreaseView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        s = StockAdjustSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        variant = ProductVariant.objects.get(id=s.validated_data["variant_id"])
        qty = s.validated_data["quantity"]
        note = s.validated_data.get("note", "")

        stock = InventoryService.increase(variant, qty, note=note)
        return Response({"on_hand": stock.on_hand, "reserved": stock.reserved}, status=status.HTTP_200_OK)


class StockDecreaseView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        s = StockAdjustSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        variant = ProductVariant.objects.get(id=s.validated_data["variant_id"])
        qty = s.validated_data["quantity"]
        note = s.validated_data.get("note", "")

        stock = InventoryService.decrease(variant, qty, note=note)
        return Response({"on_hand": stock.on_hand, "reserved": stock.reserved}, status=status.HTTP_200_OK)