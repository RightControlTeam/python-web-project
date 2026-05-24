import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import TestCase
from django_backend.users.models import User
from django_backend.store.models import Category, Product, CartItem
from django_backend.store.services.order_service import OrderService
from django_backend.store.domain.exceptions import EmptyCartError


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dima_tester', password='123')
        self.cat = Category.objects.create(name='Electronics')
        self.prod = Product.objects.create(name='Laptop', price=1000, category=self.cat)

    def test_create_order(self):
        CartItem.objects.create(user=self.user, product=self.prod, quantity=2)

        order = OrderService.create_order(self.user)

        self.assertEqual(order.total_price, 2000)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_create_order_with_empty_cart(self):
        with self.assertRaises(EmptyCartError):
            OrderService.create_order(self.user)
