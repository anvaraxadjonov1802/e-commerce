from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderMarkPaidView

urlpatterns = [
    path("orders/", OrderCreateView.as_view()),
    path("orders/list/", OrderListView.as_view()),
    path("orders/<uuid:pk>/", OrderDetailView.as_view()),

    path("orders/<uuid:pk>/mark-paid/", OrderMarkPaidView.as_view()),
]