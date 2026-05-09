import transaction
from django.db import transaction
from store.domain.exceptions import EmptyCartError
from store.models import CartItem, Order, OrderItem

from django_backend.store.domain.exceptions import OrderNotFound, OrderCancellationError
import logging

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user):
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            logger.warning(f"Попытка создания пустого заказа пользователем {user.username}")
            raise EmptyCartError("Нельзя создать заказ для пустой корзины")

        order = Order.objects.create(user=user, total_price=0, status=Order.STATUS_PENDING)
        total_price = 0

        for cart_item in cart_items:
            OrderItem.objects.create(order=order,product=cart_item.product, quantity=cart_item.quantity,price=cart_item.product.price)
            total_price += cart_item.product.price * cart_item.quantity

        order.total_price = total_price
        order.save()
        cart_items.delete()

        logger.info(f"Создан заказ {order.id} для {user.username} на сумму {total_price}")
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int):
        order = Order.objects.select_for_update().filter(id=order_id).first()

        if not order:
            logger.error(f"При отмене заказ {order_id} не был найден")
            raise OrderNotFound(f"Заказ с id {order_id} не найден")

        if order.status == Order.STATUS_CANCELLED:
            return order

        if order.status == Order.STATUS_DONE:
            logger.warning(f"Попытка отмены уже выполненного заказа {order_id}")
            raise OrderCancellationError(f"Нельзя отменить заказ в статусе {order.status}")

        order.status = Order.STATUS_CANCELLED
        order.save()

        logger.info(f"Заказ {order_id} успешно переведен в статус 'cancelled'")
        return order