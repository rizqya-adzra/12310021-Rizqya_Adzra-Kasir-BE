from django.contrib import admin
from .models import Member, Transaction, TransactionDetail

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'telephone', 'point', 'created_at')
    search_fields = ('name', 'telephone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


class TransactionDetailInline(admin.TabularInline):
    model = TransactionDetail
    extra = 0
    # Kita buat read-only agar harga dan qty tidak bisa diubah seenaknya
    readonly_fields = ('product', 'price', 'quantity', 'subtotal')
    can_delete = False

    # Mencegah penambahan detail transaksi secara manual di admin
    def has_add_permission(self, request, obj):
        return False


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # Kolom yang muncul di tabel depan
    list_display = ('invoice', 'created_at', 'user', 'customer_name', 'total')
    list_filter = ('is_member', 'created_at', 'user')
    search_fields = ('invoice', 'customer_name', 'telephone')
    
    # Menampilkan detail barang belanjaan di dalam halaman transaksi
    inlines = [TransactionDetailInline]
    
    # Mengelompokkan form agar lebih rapi dilihat
    fieldsets = (
        ('Informasi Utama', {
            'fields': ('invoice', 'user', 'created_at')
        }),
        ('Informasi Pelanggan', {
            'fields': ('is_member', 'member', 'customer_name', 'telephone')
        }),
        ('Informasi Keuangan', {
            'fields': ('payment_amount', 'subtotal', 'total', 'change_amount')
        }),
        ('Informasi Poin', {
            'fields': ('is_point', 'point')
        }),
    )

    # Mengunci semua field agar tidak bisa diedit
    readonly_fields = (
        'invoice', 'user', 'created_at', 'is_member', 'member', 
        'customer_name', 'telephone', 'payment_amount', 'subtotal', 
        'total', 'change_amount', 'is_point', 'point'
    )

    # Mencegah admin membuat nota transaksi palsu lewat Django Admin
    def has_add_permission(self, request):
        return False

    # Mencegah admin menghapus nota transaksi (opsional, jika ingin benar-benar ketat)
    def has_delete_permission(self, request, obj=None):
        return False