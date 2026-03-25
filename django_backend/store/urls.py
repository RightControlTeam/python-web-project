# store/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, CartItemViewSet

router = DefaultRouter()

router.register(r'category', CategoryViewSet)
router.register(r'product', ProductViewSet)
router.register(r'cart', CartItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]