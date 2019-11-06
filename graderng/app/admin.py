from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from app.models import Submission


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'problem_name', 'user_id',
                    'assignment_id', 'time_limit', 'memory_limit')
    search_fields = ('user_id', 'assignment_idb')


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


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Submission, SubmissionAdmin)
