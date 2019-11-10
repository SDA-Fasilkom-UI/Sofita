from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from app import tasks
from app.models import Submission, Token


class AdminActions():
    """
    This is a class that's used only as a container
    for functions/actions that need to be used by other ModelAdmin
    below.
    """

    def submission_regrade(modeladmin, request, queryset):
        for submission in queryset.all():
            result = tasks.grade.delay(submission.id, submission.assignment_id,
                                       submission.user_id, submission.attempt_number)

        modeladmin.message_user(
            request, "Selected submission will be regraded")


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
    list_display = ("id", "id_number", "problem_name",
                    "attempt_number", "assignment_id", "user_id")
    actions = [AdminActions.submission_regrade]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Token, TokenAdmin)
