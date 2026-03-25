# store/views.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.action ==  "create":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "destroy":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    http_method_names = ['get', 'post', 'delete']


class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['category']
    search_fields = ['name']
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    http_method_names = ['get', 'post', 'delete', 'put', 'patch']