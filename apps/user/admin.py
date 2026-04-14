from django.contrib import admin
from .models import CoreUser

@admin.register(CoreUser)
class CoreUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'created_at')
    
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    
    fieldsets = (
        ('Informasi Utama', {
            'fields': ('email', 'username', 'role', 'image')
        }),
        ('Hak Akses', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Riwayat Waktu', {
            'fields': ('last_login', 'created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('last_login', 'created_at', 'updated_at')

    ordering = ('-created_at',)