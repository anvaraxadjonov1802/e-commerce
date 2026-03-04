from django.db import models
import uuid
from django.conf import settings
from catalog.models import ProductVariant


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    total_amount = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def recalculate_total(self):
        total = sum(i.total_amount for i in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items',
    )

    #SNAPSHOT
    product_title = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    attributes_text = models.CharField(max_length=255)

    unit_price_amount = models.PositiveBigIntegerField()
    unit_discount_amount = models.PositiveBigIntegerField(default=0)

    quantity = models.PositiveIntegerField()
    total_amount = models.PositiveBigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):

        #snapshot copy
        if not self.product_title:
            self.product_title = self.variant.product.title
        if not self.sku:
            self.sku = self.variant.sku
        if not self.attributes_text:
            self.attributes_text = self.variant.attributes_text
        if self.unit_price_amount is None:
            self.unit_price_amount = self.variant.price_amount
        if self.unit_discount_amount is None:
            self.unit_discount_amount = 0

        self.total_amount = (self.unit_price_amount - self.unit_discount_amount) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_title} x {self.quantity}"