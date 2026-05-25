import os
import django
from decimal import Decimal
from unittest.mock import patch


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django_backend.users.models import User
from django_backend.store.models import Category, Product, CartItem, Order
from django_backend.store.services.product_service import ProductService
from django_backend.store.services.cart_service import CartService
from django_backend.store.services.order_service import OrderService
from django_backend.store.services.transaction_client import TransactionClient
from django_backend.store.domain.exceptions import (
    ProductNotFound, ProductValidationError, ProductAlreadyExists, CartItemNotFound,
    EmptyCartError, BalanceError, OrderCancellationError, CartValidationError
)


class ProductServiceTest(TestCase):
    """Тестирование ProductService"""

    def setUp(self):
        self.category = Category.objects.create(name="Электроника")
        self.product = Product.objects.create(
            name="Смартфон",
            price=Decimal("50000.00"),
            category=self.category,
            stock=10
        )

    def test_get_product_by_id(self):
        product = ProductService.get_product_by_id(self.product.id)
        self.assertEqual(product.name, "Смартфон")

    def test_get_product_by_fake_id(self):
        with self.assertRaises(ProductNotFound):
            ProductService.get_product_by_id(999)

    def test_get_products_filtering(self):
        Product.objects.create(name="Ноутбук", price=Decimal("90000.00"), category=self.category, stock=5)

        products = ProductService.get_products(category_id=self.category.id, search="Ноут")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Ноутбук")

    def test_create_product(self):
        new_prod = ProductService.create_product(
            name="Наушники",
            price=Decimal("5000.00"),
            category_id=self.category.id,
            stock=100
        )
        self.assertEqual(Product.objects.filter(name="Наушники").count(), 1)

    def test_create_product_validation(self):
        with self.assertRaises(ProductValidationError):
            ProductService.create_product(name="", price=Decimal("-10"), category_id=self.category.id)

    def test_create_exists_product(self):
        with self.assertRaises(ProductAlreadyExists):
            ProductService.create_product(name="Смартфон", price=Decimal("50000.00"), category_id=self.category.id)

    def test_update_product_success(self):
        updated_prod = ProductService.update_product(
            pk=self.product.id,
            name="Тест",
            price=Decimal("55000.00"),
            stock=15
        )
        self.assertEqual(updated_prod.name, "Тест")
        self.assertEqual(updated_prod.price, Decimal("55000.00"))
        self.assertEqual(updated_prod.stock, 15)

    def test_delete_product_success(self):
        ProductService.delete_product(self.product.id)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

class CartServiceTest(TestCase):
    """Тестирование CartService"""

    def setUp(self):
        self.user = User.objects.create_user(username="cart_user", password="password123")
        self.category = Category.objects.create(name="Книги")
        self.product = Product.objects.create(name="Книга", price=Decimal("1500.00"), category=self.category,                                              stock=20)

    def test_add_product_to_cart(self):
        cart_item, product = CartService.add_product_to_cart(self.user, self.product.id, quantity=2)
        self.assertEqual(cart_item.quantity, 2)

        cart_item, _ = CartService.add_product_to_cart(self.user, self.product.id, quantity=3)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_delete_product_from_cart(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        CartService.delete_product_from_cart(self.user, self.product.id)
        self.assertFalse(CartItem.objects.filter(user=self.user, product=self.product).exists())

    def test_delete_product_not_in_cart(self):
        with self.assertRaises(CartItemNotFound):
            CartService.delete_product_from_cart(self.user, self.product.id)

    def test_update_product(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=5)
        CartService.update_product_quantity(self.user, self.product.id, quantity=0)
        self.assertFalse(CartItem.objects.filter(user=self.user, product=self.product).exists())

    def test_clear_cart(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        deleted_count = CartService.clear_cart(self.user)
        self.assertEqual(deleted_count, 1)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_get_total_price(self):
        prod2 = Product.objects.create(name="Блокнот", price=Decimal("500.00"), category=self.category, stock=10)
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        CartItem.objects.create(user=self.user, product=prod2, quantity=3)

        total = CartService.get_total_price(self.user)
        self.assertEqual(total, Decimal("4500.00"))

    def test_delete_product_validation(self):
        with self.assertRaises(CartValidationError):
            CartService.delete_product_from_cart(user=None, product_id=self.product.id)

        with self.assertRaises(CartValidationError):
            CartService.delete_product_from_cart(user=self.user, product_id=None)
class OrderServiceTest(TestCase):
    """Тестирование OrderService"""

    def setUp(self):
        self.user = User.objects.create_user(username="order_user", password="password123")
        self.user.balance = Decimal("10000.00")
        self.user.save()

        self.category = Category.objects.create(name="Одежда")
        self.product = Product.objects.create(name="Худи", price=Decimal("3000.00"), category=self.category, stock=5)

    def test_create_order_empty_cart(self):
        with self.assertRaises(EmptyCartError):
            OrderService.create_order(self.user)

    def test_create_order_more_balance(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=5)

        with self.assertRaises(BalanceError):
            OrderService.create_order(self.user)

    @patch('django_backend.store.services.order_service.TransactionClient.create_transaction')
    @patch('django_backend.store.services.order_service.settings')
    def test_create_order_with_token(self, mock_settings, mock_create_transaction):
        mock_settings.DEBUG = False
        mock_create_transaction.return_value = {"success": True, "transaction": {"id": 123}}

        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        order = OrderService.create_order(self.user, auth_token="mocked_token")

        self.assertEqual(order.status, Order.STATUS_PAID)

    def test_cancel_order(self):
        order = Order.objects.create(user=self.user, total_price=Decimal("2000.00"), status=Order.STATUS_PENDING)

        cancelled_order = OrderService.cancel_order(order.id)
        self.assertEqual(cancelled_order.status, Order.STATUS_CANCELLED)

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("12000.00"))

    def test_cancel_already_paid_order_raises_error(self):
        order = Order.objects.create(user=self.user, total_price=Decimal("2000.00"), status=Order.STATUS_PAID)

        with self.assertRaises(OrderCancellationError):
            OrderService.cancel_order(order.id)


class TransactionClientTest(TestCase):
    """Тестирование TransactionClient"""

    @patch('django_backend.store.services.transaction_client.requests.post')
    def test_create_transaction_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 777, "status": "processed"}

        res = TransactionClient.create_transaction(order_id=1, amount=5000.0, auth_token="valid_token")

        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 201)
        self.assertEqual(res["transaction"]["id"], 777)

        mock_post.assert_called_once()

    @patch('django_backend.store.services.transaction_client.requests.post')
    def test_create_transaction_api_error(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 400
        mock_response.text = "Invalid token or expired"

        res = TransactionClient.create_transaction(order_id=1, amount=5000.0, auth_token="bad_token")

        self.assertFalse(res["success"])
        self.assertEqual(res["status_code"], 400)
        self.assertEqual(res["transaction"], "Invalid token or expired")

