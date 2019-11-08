from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from app.models import Submission, Token


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        ('', {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, user, form, change):
        if request.user.is_superuser:
            user.is_staff = user.is_superuser
            user.save()


class TokenAdmin(admin.ModelAdmin):
    list_display = ("token", "service")
    search_fields = ("token", "service")
    readonly_fields = ("token",)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id_number", "problem_name",
                    "attempt_number", "assignment_id", "user_id")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Token, TokenAdmin)
