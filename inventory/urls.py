from django.urls import path
from .views import StockIncreaseView, StockDecreaseView

urlpatterns = [
    path("admin/stock/increase/", StockIncreaseView.as_view()),
    path("admin/stock/decrease/", StockDecreaseView.as_view()),
]