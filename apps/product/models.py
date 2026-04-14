from django.db import models
from django.conf import settings
from utils.models import UUIDModel
from utils.sku import generate_sku 


class Category(UUIDModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'prd_categories'
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return f"{self.name}"


class Product(UUIDModel):
    VISIBILITY_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('admin only', 'Admin Only'),
    ]

    sku = models.CharField(max_length=255, unique=True, blank=True, editable=False)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    minimal_stock = models.PositiveIntegerField(default=0)
    
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='draft')

    class Meta:
        db_table = 'prd_products'
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"[{self.sku}] {self.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = generate_sku(Product)
        super(Product, self).save(*args, **kwargs)
        
    @property
    def is_low_stock(self):
        return self.stock <= self.minimal_stock