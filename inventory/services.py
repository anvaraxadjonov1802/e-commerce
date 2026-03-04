from django.db import transaction
from django.core.exceptions import ValidationError

from .models import StockItem, StockMovement


class InventoryService:

    @staticmethod
    @transaction.atomic
    def increase(variant, qty, note=""):
        if qty <= 0:
            raise ValidationError("qty must be positive")

        stock, _ = StockItem.objects.select_for_update().get_or_create(variant=variant)
        stock.on_hand += qty
        stock.save(update_fields=["on_hand"])

        StockMovement.objects.create(
            stock_item=stock,
            type=StockMovement.Type.IN,
            quantity=qty,
            note=note
        )
        return stock

    @staticmethod
    @transaction.atomic
    def decrease(variant, qty, note=""):
        if qty <= 0:
            raise ValidationError("qty must be positive")

        stock = StockItem.objects.select_for_update().get(variant=variant)
        available = stock.on_hand - stock.reserved
        if qty > available:
            raise ValidationError("not enough stock available")

        stock.on_hand -= qty
        stock.save(update_fields=["on_hand"])

        StockMovement.objects.create(
            stock_item=stock,
            type=StockMovement.Type.OUT,
            quantity=qty,
            note=note
        )
        return stock

    @staticmethod
    @transaction.atomic
    def reserve(variant, qty, note=""):
        stock = StockItem.objects.select_for_update().get(variant=variant)

        available = stock.on_hand - stock.reserved
        if qty > available:
            raise ValidationError("Not enough stock to reserve")

        stock.reserved += qty
        stock.save(update_fields=["reserved"])

        StockMovement.objects.create(
            stock_item=stock,
            type=StockMovement.Type.ADJUST,
            quantity=qty,
            note=f"Reserve: {note}"
        )

        return stock

    @staticmethod
    @transaction.atomic
    def release(variant, qty, note=""):
        stock = StockItem.objects.select_for_update().get(variant=variant)

        if qty > stock.reserved:
            raise ValidationError("Release qty exceeds reserved")

        stock.reserved -= qty
        stock.save(update_fields=["reserved"])

        StockMovement.objects.create(
            stock_item=stock,
            type=StockMovement.Type.ADJUST,
            quantity=qty,
            note=f"Release: {note}"
        )

        return stock