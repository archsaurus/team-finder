from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'surname', 'phone', 'is_active']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'name', 'surname', 'phone']
    ordering = ['email']

    fieldsets = (
        ('Основное', {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('name', 'surname', 'phone')}),
        ('Профиль', {'fields': ('avatar', 'about', 'github_url')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'surname',
                    'phone',
                )
            },
        ),
    )
    readonly_fields = ['avatar']
