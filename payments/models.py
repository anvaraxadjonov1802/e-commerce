import uuid
from django.db import models
from orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    provider = models.CharField(max_length=50)  # click / payme / etc
    transaction_id = models.CharField(max_length=255, unique=True)

    amount = models.PositiveBigIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.provider} | {self.transaction_id}"