#store/serializers.py

from rest_framework import serializers
from .models import Product, Category, CartItem, Order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'user']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество товара должно быть больше 0.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'created_at']