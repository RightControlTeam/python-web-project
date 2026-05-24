from django.db import models
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ('transaction', 'Транзакция'),
        ('payment_success', 'Успешная оплата'),
        ('payment_failed', 'Ошибка оплаты'),
        ('order_cancelled', 'Заказ отменён'),
        ('system', 'Системное уведомление'),
    ]
    
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    transaction_id = models.IntegerField(null=True, blank=True, db_index=True)
    order_id = models.IntegerField(null=True, blank=True, db_index=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    
    success = models.BooleanField(default=False)
    cost = models.IntegerField(null=True, blank=True)
    message = models.TextField()
    
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_processed', '-created_at']),]
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
    
    def __str__(self):
        return f"Notification #{self.id} - {self.notification_type}"
    
    def mark_as_processed(self):
        if not self.is_processed:
            self.is_processed = True
            self.processed_at = timezone.now()
            self.save(update_fields=['is_processed', 'processed_at'])