from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_backend.store.api.views import (
    CategoryViewSet,
    ProductViewSet,
    CartItemViewSet,
    OrderViewSet
)

router = DefaultRouter()

router.register(r'category', CategoryViewSet)
router.register(r'product', ProductViewSet)
router.register(r'cart', CartItemViewSet)
router.register(r'order', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]