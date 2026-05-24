from django.shortcuts import render

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from shared.config import settings

from .models import Notification

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def notification_webhook(request):
    notification_key = request.headers.get('X-Notification-Key')
    expected_key = getattr(settings, 'NOTIFICATION_KEY', None)
    
    if not expected_key:
        return JsonResponse({'error': 'Server configuration error'}, status=500)
    
    if notification_key != expected_key:
        logger.warning(f"Неверный ключ уведомления: {notification_key}")
        return JsonResponse({'error': 'Invalid notification key'}, status=401)

    try:
        data = json.loads(request.body)
        logger.info(f"Получено уведомление: {data}")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    notification_type = 'payment_success' if data.get('success') else 'payment_failed'

    notification = Notification.objects.create(
        notification_type=notification_type,
        transaction_id=data.get('transaction_id'),
        order_id=data.get('order_id'),
        user_id=data.get('user_id'),
        success=data.get('success', False),
        cost=data.get('cost'),
        message=data.get('message', ''),
        is_processed=False
    )

    # Используем метод mark_as_processed
    notification.mark_as_processed()

    return JsonResponse({'status': 'ok', 'notification_id': notification.id})