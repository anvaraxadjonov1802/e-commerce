import uuid
from django.db import models
from catalog.models import ProductVariant

class StockItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock"
    )

    on_hand = models.PositiveIntegerField(default=0)  # real bor
    reserved = models.PositiveIntegerField(default=0) # band qilingan (keyin order’da ishlatamiz)

    updated_at = models.DateTimeField(auto_now=True)

    def available(self):
        return self.on_hand - self.reserved

    def __str__(self):
        return f"{self.variant.sku} | on_hand={self.on_hand} reserved={self.reserved}"


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"
        ADJUST = "adjust", "Adjust"
        RETURN = "return", "Return"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    type = models.CharField(max_length=20, choices=Type.choices)
    quantity = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_item.variant.sku} {self.type} {self.quantity}"
