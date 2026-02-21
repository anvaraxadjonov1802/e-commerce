from django.urls import path
from .views import RegisterView, MeView, TelegramAuthView
urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("me/", MeView.as_view()),

    path("telegram-auth/", TelegramAuthView.as_view()),

]