from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={
            'required': 'Nama kategori wajib diisi.',
            'blank': 'Nama kategori tidak boleh kosong.',
            'invalid': 'Format nama kategori tidak valid.'
        }
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={
            'required': 'Nama produk wajib diisi.',
            'blank': 'Nama produk tidak boleh kosong.'
        }
    )
    price = serializers.IntegerField(
        error_messages={
            'required': 'Harga produk wajib diisi.',
            'invalid': 'Format harga harus berupa angka bulat.'
        }
    )

    is_low_stock = serializers.ReadOnlyField()

    category = serializers.StringRelatedField(read_only=True)
    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category', 
        error_messages={
            'required': 'Kategori wajib dipilih.',
            'null': 'Kategori tidak boleh kosong.',
            'does_not_exist': 'Kategori yang dipilih tidak ditemukan.',
            'incorrect_type': 'Format ID kategori tidak valid.' 
        }
    )
    visibility = serializers.ChoiceField(
        choices=Product.VISIBILITY_CHOICES,
        default='draft',
        error_messages={
            'invalid_choice': 'Pilihan visibilitas tidak valid.'
        }
    )

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'user', 'category', 'category_id', 'name', 'description', 
            'price', 'stock', 'minimal_stock', 'image', 'visibility', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sku', 'user', 'created_at', 'updated_at']
        
class AddStockSerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        min_value=1, 
        error_messages={
            'min_value': 'Jumlah penambahan stok minimalnya 1. Tidak dapat mengurangi stok dari sini.'
        }
    )