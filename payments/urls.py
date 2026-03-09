from django.urls import path
from .views import PaymentCreateView, PaymentWebhookView, ManualPaymentCreateView, AdminPaymentConfirmView

urlpatterns = [
    path("payments/create/", PaymentCreateView.as_view()),
    path("payments/webhook/", PaymentWebhookView.as_view()),
    path("payments/manual/create/", ManualPaymentCreateView.as_view()),
    path("admin/payments/confirm/", AdminPaymentConfirmView.as_view()),
]