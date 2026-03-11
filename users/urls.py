from django.urls import path
from .views import RegisterView, MeView, TelegramCheckView, TelegramBindView, TelegramLoginView
urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("me/", MeView.as_view()),
    path("telegram-check/", TelegramCheckView.as_view()),
    path("telegram-bind/", TelegramBindView.as_view()),
    path("telegram-login/", TelegramLoginView.as_view()),
]
