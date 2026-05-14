from store.models import CartItem, Product
from users.models import User
from django.db import transaction
from django.db.models import F
from store.domain.exceptions import ProductNotFound, CartItemNotFound, CartValidationError


class CartService:
    @staticmethod
    def add_product_to_cart(user, product_id, quantity=1):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ProductNotFound(f"Товар с id {product_id} не найден")

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()

        return cart_item, product

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