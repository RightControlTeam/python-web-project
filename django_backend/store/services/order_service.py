from django.db import transaction
from django_backend.store.domain.exceptions import EmptyCartError
from django_backend.store.models import CartItem, Order, OrderItem
from django_backend.store.services.transaction_client import TransactionClient
from django_backend.store.domain.exceptions import OrderNotFound, OrderCancellationError, BalanceError, TokenNotFound, TransactionError
import logging

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, auth_token):
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            raise EmptyCartError("Нельзя создать заказ для пустой корзины")

        order = Order.objects.create(user=user, total_price=0)
        total_price = 0

        for cart_item in cart_items:
            OrderItem.objects.create(order=order,product=cart_item.product, quantity=cart_item.quantity,price=cart_item.product.price)
            total_price += cart_item.product.price * cart_item.quantity

        if total_price > user.balance:
            logger.warning("Not enough money")
            raise BalanceError(f"Not enough money, your balance: {user.balance}, need {total_price}")

        order.total_price = total_price
        order.status = Order.STATUS_PENDING
        if not auth_token:
            logger.warning("No auth token")
            raise TokenNotFound("Token is required")
        else:
            res = TransactionClient.create_transaction(order_id=order.id, amount=total_price, auth_token=auth_token)
            if not res.get("success"):
                logger.error(f"Transaction failed. {res.get("error")}")
                order.delete()
                raise TransactionError(f"Transaction failed: {res.get("error")}. Please, try again later")

            transaction_data = res.get("transaction")
            logger.info(f"Transaction {transaction_data.get('id')} created successfully")
            order.status=Order.STATUS_PAID
            user.balance -= total_price
            user.save()
            logger.info(f"Order is paid")

        order.save()
        cart_items.delete()
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int):
        order = Order.objects.select_for_update().filter(id=order_id).first()

        if not order:
            raise OrderNotFound(f"Заказ с id {order_id} не найден")

        if order.status == Order.STATUS_CANCELLED:
            return order

        if order.status in [Order.STATUS_PAID, Order.STATUS_DONE]:
            raise OrderCancellationError(f"Нельзя отменить заказ в статусе {order.status}")

        order.user.balance += order.total_price
        order.status = Order.STATUS_CANCELLED
        order.save()
        logger.info(f"Order {order_id} is cancelled")
        return order