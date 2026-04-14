from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'sku', 
        'name', 
        'category', 
        'price', 
        'stock', 
        'visibility', 
        'user'
    )
    
    list_filter = ('visibility', 'category', 'created_at')
    
    search_fields = ('sku', 'name', 'description')
    
    readonly_fields = ('sku', 'user', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('sku', 'name', 'category', 'description', 'user')
        }),
        ('Inventaris & Harga', {
            'fields': ('price', 'stock', 'minimal_stock')
        }),
        ('Media & Status', {
            'fields': ('image', 'visibility')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), 
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)