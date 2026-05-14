from decimal import Decimal
from typing import Optional
from django.db import transaction
import logging

from store.models import Product, Category
from store.domain.exceptions import (
    ProductNotFound,
    ProductAlreadyExists,
    ProductValidationError,
    ProductCategoryNotFound
)
logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def get_product_by_id(product_id: int) -> Product:
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ProductNotFound(f"Product with id {product_id} does not exist")
        return product


    @staticmethod
    def get_products(
            category_id: Optional[int] = None,
            search: Optional[str] = None,
            offset: int = 0,
            page_length: int = 20
    ) -> list[Product]:
        if offset < 0: offset = 0
        if page_length < 1: page_length = 1
        queryset = Product.objects.select_related("category").order_by("id", "name")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return  list(queryset[offset : offset + page_length])


    @staticmethod
    @transaction.atomic
    def create_product(
        name: str,
        price: Decimal,
        category_id: int,
        stock: int = 0
    ) -> Product:

        if not name:
            raise ProductValidationError("Product name cannot be empty")
        if price <= 0:
            raise ProductValidationError("Product price must be greater than 0")
        if stock < 0:
            raise ProductValidationError("Product stock cannot be negative")

        logger.info(f"Создание нового товара: {name}, цена: {price}, склад: {stock}")

        if Product.objects.filter(name = name).exists():
            logger.error(f"Ошибка создания: товар '{name}' уже существует")
            raise ProductAlreadyExists(f"Product with name {name} already exists")
        if not Category.objects.filter(id = category_id).exists():
            logger.error(f"Ошибка создания: категории с айди {category_id} не существует")
            raise ProductCategoryNotFound(f"Category with id {category_id} does not exist")

        return Product.objects.create(
            name = name,
            price = price,
            category_id = category_id,
            stock = stock,
        )


    @staticmethod
    @transaction.atomic
    def update_product(
        pk: int,
        name: Optional[str] = None,
        price: Optional[Decimal] = None,
        category_id: Optional[int] = None,
        stock: Optional[int] = None
    ):
        product = Product.objects.select_for_update().filter(id=pk).first()
        if not product:
            logger.error(f" Товар ID {pk} не найден")
            raise ProductNotFound(f"Product with id {pk} does not exist")

        if name is not None:
            if not name:
                raise ProductValidationError("Product name cannot be empty")
            if Product.objects.filter(name = name).exclude(id=pk).exists():
                logger.warning(f" Имя '{name}' уже занято другим товаром")
                raise ProductAlreadyExists(f"Product with name {name} already exists")
            product.name = name

        if price is not None:
            if price <= 0:
                raise ProductValidationError("Product price must be greater than 0")
            logger.info(f"Изменение цены товара {pk}: {product.price} -> {price}")
            product.price = price

        if stock is not None:
            if stock < 0:
                raise ProductValidationError("Product stock cannot be negative")
            logger.info(f" Обновление склада товара {pk}: {product.stock} -> {stock}")
            product.stock = stock

        if category_id is not None:
            if not Category.objects.filter(id=category_id).exists():
                logger.error(f" Категории с id {category_id} не существует")
                raise ProductCategoryNotFound(f"Category with id {category_id} does not exist")
            product.category_id = category_id

        product.save()
        logger.info(f"Товар ID {pk} успешно обновлен")
        return product


    @staticmethod
    @transaction.atomic
    def delete_product(pk: int):
        product = Product.objects.select_for_update().filter(id=pk).first()
        if product:
            logger.info(f"Удаление товара ID {pk} ({product.name})")
            product.delete()
        else:
            logger.warning(f"Попытка удаления несуществующего товара ID {pk}")
            raise ProductNotFound(f"Product with id {pk} does not exist")