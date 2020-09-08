from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from app.models import Token


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser',)


class TokenAdmin(admin.ModelAdmin):
    list_display = ("token", "service")
    search_fields = ("token", "service")
    readonly_fields = ("token",)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Token, TokenAdmin)
