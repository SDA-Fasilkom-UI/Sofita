from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from app.models import Token


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser',)


class UserInline(admin.TabularInline):
    model = User.groups.through


class CustomGroupAdmin(GroupAdmin):
    inlines = [UserInline, ]


class TokenAdmin(admin.ModelAdmin):
    list_display = ("token", "service")
    search_fields = ("token", "service")
    readonly_fields = ("token",)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

admin.site.register(Token, TokenAdmin)
