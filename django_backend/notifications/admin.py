from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'notification_type', 'order_id', 'transaction_id', 'success', 'is_processed', 'created_at']
    list_filter = ['notification_type', 'success', 'is_processed', 'created_at']
    search_fields = ['order_id', 'transaction_id', 'message']
    readonly_fields = ['created_at', 'processed_at']