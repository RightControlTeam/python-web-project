from store.models import CartItem, Product
from django.db.models import F

from django_backend.store.domain.exceptions import ProductNotFound


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