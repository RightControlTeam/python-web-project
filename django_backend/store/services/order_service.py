import transaction
from django.db import transaction
from store.domain.exceptions import EmptyCartError
from store.models import CartItem, Order, OrderItem

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