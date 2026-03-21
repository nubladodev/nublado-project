from django.urls import path

from .views import BotWebhookView

app_name = "django_telegram"

urlpatterns = [
    path(
        "<bot_id>/webhook/",
        BotWebhookView.as_view(),
        name="bot_webhook_view",
    ),
]
