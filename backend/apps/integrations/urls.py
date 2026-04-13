from django.urls import path
from .views import TelegramLinkView

urlpatterns = [
    path("telegram/link/", TelegramLinkView.as_view()),
]
