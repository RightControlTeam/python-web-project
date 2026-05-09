import logging
from store.models import CartItem, Product
from django.db.models import F

from django_backend.store.domain.exceptions import ProductNotFound

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def add_product_to_cart(user, product_id, quantity=1):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            logger.error(f" Товар ID {product_id} не найден при добавлении в корзину пользователя {user.username}")
            raise ProductNotFound(f"Товар с id {product_id} не найден")

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            logger.info(f"Увеличение количества товара '{product.name}' в корзине пользователя {user.username}")
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()
            cart_item.refresh_from_db()
        else:
            logger.info(f"Товар {product.name} добавлен в корзину пользователя {user.username}")
        return cart_item, product