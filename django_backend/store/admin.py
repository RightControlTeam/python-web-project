from django.contrib import admin
from .models import Category, Product, CartItem, Order

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
