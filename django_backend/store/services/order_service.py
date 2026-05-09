import transaction
from django.db import transaction
from store.domain.exceptions import EmptyCartError
from store.models import CartItem, Order, OrderItem

from django_backend.store.domain.exceptions import OrderNotFound, OrderCancellationError


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user):
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            raise EmptyCartError("Нельзя создать заказ для пустой корзины")

        order = Order.objects.create(user=user, total_price=0, status='new')
        total_price = 0

        for cart_item in cart_items:
            OrderItem.objects.create(order=order,product=cart_item.product, quantity=cart_item.quantity,price=cart_item.product.price)
            total_price += cart_item.product.price * cart_item.quantity

        order.total_price = total_price
        order.save()
        cart_items.delete()
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int):
        order = Order.objects.select_for_update().filter(id=order_id).first()

        if not order:
            raise OrderNotFound(f"Заказ с id {order_id} не найден")

        if order.status == 'cancelled':
            return order

        if order.status in ['delivered', 'shipped']:
            raise OrderCancellationError(f"Нельзя отменить заказ в статусе {order.status}")

        order.status = 'cancelled'
        order.save()

        return order