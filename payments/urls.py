from django.urls import path
from .views import PaymentCreateView, PaymentWebhookView

urlpatterns = [
    path("payments/create/", PaymentCreateView.as_view()),
    path("payments/webhook/", PaymentWebhookView.as_view()),
]