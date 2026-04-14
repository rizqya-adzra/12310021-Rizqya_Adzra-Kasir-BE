from django.urls import path
from apps.product.views import CategoryDetailView, CategoryListCreateView, ProductAddStockView, ProductDetailView, ProductListCreateView

urlpatterns = [
    path('products/categories/', CategoryListCreateView.as_view(), name='login'),
    path('products/categories/<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/list/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/list/detail/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<uuid:pk>/add-stock/', ProductAddStockView.as_view(), name='product-add-stock'),
]