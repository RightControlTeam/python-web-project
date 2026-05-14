import transaction
from django.db import transaction
from store.domain.exceptions import EmptyCartError
from store.models import CartItem, Order, OrderItem, Product

from store.domain.exceptions import OrderNotFound, OrderCancellationError


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

    @staticmethod
    @transaction.atomic
    def delete_product_from_cart(user: User, product_id: int):
        if not user:
            raise CartValidationError("Field user is required")

        if not product_id:
            raise CartValidationError("Field product_id is required")

        if product_id <= 0:
            raise CartValidationError("Product id must be greater than 0")

        product = Product.objects.filter(id=product_id).first()

        if not product:
            raise ProductNotFound(f"Product with id {product_id} does not exist")

        cart_item = CartItem.objects.select_for_update().filter(product_id=product_id, user=user).first()

        if not cart_item:
            raise CartItemNotFound(f"Product with id {product_id} is not in the cart")

        cart_item.delete()