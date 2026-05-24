from django.urls import path
from . import views

urlpatterns = [
    path('transaction-notify/', views.notification_webhook, name='transaction-notify'),
]