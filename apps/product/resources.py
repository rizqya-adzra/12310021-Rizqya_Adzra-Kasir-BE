from import_export import resources
from apps.product.models import Category, Product

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name', 'sku', 'price', 'stock', 'category', 'status') 

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('name', 'description') 