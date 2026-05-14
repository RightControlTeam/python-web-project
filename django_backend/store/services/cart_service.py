from store.models import CartItem, Product
from users.models import User
from django.db import transaction
from django.db.models import F
from store.domain.exceptions import ProductNotFound, CartItemNotFound, CartValidationError
import logging

logger = logging.getLogger(__name__)


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
            logger.error("User is none")
            raise CartValidationError("Field user is required")

        if not product_id:
            logger.warning(f"Попытка удаления товара без id")
            raise CartValidationError("Field product_id is required")

        if product_id <= 0:
            raise CartValidationError("Product id must be greater than 0")

        product = Product.objects.filter(id=product_id).first()

        if not product:
            logger.warning(f"Попытка удаления несуществующего товара {product_id} пользователем {user.id}")
            raise ProductNotFound(f"Product with id {product_id} does not exist")

        cart_item = CartItem.objects.select_for_update().filter(product_id=product_id, user=user).first()

        if not cart_item:
            logger.warning(f"Пользователь {user.id} попытался удалить товар {product_id}, которого нет в корзине")
            raise CartItemNotFound(f"Product with id {product_id} is not in the cart")

        cart_item.delete()


    @staticmethod
    @transaction.atomic
    def update_product_quantity(user: User, product_id: int, quantity: int):
        if not user:
            logger.error("User is none")
            raise CartValidationError("Field user is required")

        if not product_id:
            logger.warning(f"Попытка обновления товара без id")
            raise CartValidationError("Field product_id is required")

        if product_id <= 0:
            raise CartValidationError("Product id must be greater than 0")

        if quantity < 0:
            raise CartValidationError("Quantity cannot be negative")

        product = Product.objects.filter(id=product_id).first()
        if not product:
            logger.warning(f"Попытка удаления несуществующего товара {product_id} пользователем {user.id}")
            raise ProductNotFound(f"Product with id {product_id} does not exist")

        cart_item = CartItem.objects.select_for_update().filter(product_id=product_id, user=user).first()
        if not cart_item:
            logger.warning(f"Пользователь {user.id} попытался обновить товар {product_id}, которого нет в корзине")
            raise CartItemNotFound(f"Product with id {product_id} does not exist")

        if quantity == 0:
            cart_item.delete()
            return None
        else:
            cart_item.quantity = quantity
            cart_item.save()
            logger.info("Пользователь успешно обновил товар")
        return cart_item