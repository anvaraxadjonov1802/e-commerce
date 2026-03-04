from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Order
from inventory.services import InventoryService
from inventory.models import StockItem, StockMovement



class OrderService:

    @staticmethod
    @transaction.atomic
    def mark_as_paid(order: Order):
        # 1) Status check
        if order.status == Order.Status.PAID:
            # idempotent variant xohlasang: return order
            raise ValidationError("Order already paid")

        if order.status != Order.Status.PENDING:
            raise ValidationError("Only pending orders can be paid")

        # 2) Itemsni olib olamiz
        items = order.items.select_related("variant").all()
        if not items.exists():
            raise ValidationError("Order has no items")

        # 3) Har bir variant stockini lock qilib, tekshirib chiqamiz
        for item in items:
            stock = (
                StockItem.objects
                .select_for_update()
                .get(variant=item.variant)
            )

            # reserved yetarlimi?
            if stock.reserved < item.quantity:
                raise ValidationError(
                    f"Reserved stock not enough for {item.variant.sku}. "
                    f"reserved={stock.reserved}, need={item.quantity}"
                )

            # on_hand yetarlimi? (reserved bo‘lsa ham, on_hand manfiy bo‘lib ketmasin)
            if stock.on_hand < item.quantity:
                raise ValidationError(
                    f"On-hand stock not enough for {item.variant.sku}. "
                    f"on_hand={stock.on_hand}, need={item.quantity}"
                )

            # 4) Paid bo‘lganda: on_hand va reserved ikkalasi ham kamayadi
            stock.on_hand -= item.quantity
            stock.reserved -= item.quantity
            stock.save(update_fields=["on_hand", "reserved"])

            # 5) Movement log (audit)
            StockMovement.objects.create(
                stock_item=stock,
                type=StockMovement.Type.OUT,
                quantity=item.quantity,
                note=f"Order {order.id} paid"
            )

        # 6) Order status paid
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])

        return order

    @staticmethod
    def mark_as_shipped(order: Order):
        if order.status != Order.Status.PAID:
            raise ValidationError("Only paid orders can be shipped")

        order.status = Order.Status.SHIPPED
        order.save(update_fields=["status"])
        return order

    @staticmethod
    def mark_as_completed(order: Order):
        if order.status != Order.Status.SHIPPED:
            raise ValidationError("Only shipped orders can be completed")

        order.status = Order.Status.COMPLETED
        order.save(update_fields=["status"])
        return order

    @staticmethod
    @transaction.atomic
    def cancel(order: Order):
        # 1) Status check
        if order.status == Order.Status.CANCELED:
            # idempotent bo‘lsin desang: return order
            raise ValidationError("Order already canceled")

        if order.status != Order.Status.PENDING:
            raise ValidationError("Only pending orders can be cancelled")

        items = order.items.select_related("variant").all()

        # 2) Reserved ni qaytarish
        for item in items:
            stock = (
                StockItem.objects
                .select_for_update()
                .get(variant=item.variant)
            )

            if stock.reserved < item.quantity:
                raise ValidationError(
                    f"Cannot release reserved for {item.variant.sku}. "
                    f"reserved={stock.reserved}, need={item.quantity}"
                )

            stock.reserved -= item.quantity
            stock.save(update_fields=["reserved"])

            # 3) Movement log
            StockMovement.objects.create(
                stock_item=stock,
                type=StockMovement.Type.ADJUST,
                quantity=item.quantity,
                note=f"Reserve released: Order {order.id} cancelled"
            )

        # 4) Status cancel
        order.status = Order.Status.CANCELED
        order.save(update_fields=["status"])

        return order