from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.notification_webhook, name='notification_webhook'),
]