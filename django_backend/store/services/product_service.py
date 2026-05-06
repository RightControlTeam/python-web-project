from store.domain.exceptions import ProductNotFound
from store.models import Product
from typing import Optional

class ProductService:
    @staticmethod
    def get_product_by_id(product_id: int) -> Product:
        try:
            product = Product.objects.get(id=product_id)
            return product
        except Product.DoesNotExist:
            raise ProductNotFound(f"Product with id {product_id} does not exist")


    @staticmethod
    def get_products(
            category_id: Optional[int] = None,
            search: Optional[str] = None,
            offset: int = 0,
            page_length: int = 20
    ) -> list[Product]:
        queryset = Product.objects.select_related("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search:
            queryset = queryset.filter(name__icontains=search)

        queryset = queryset.order_by("id", "name")

        return  list(queryset[offset : offset + page_length])