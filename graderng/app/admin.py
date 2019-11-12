from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

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


# https://medium.com/@hakibenita/how-to-add-a-text-filter-to-django-admin-5d1db93772d8
class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'
    model_admin = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model_admin = model_admin

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class AssignmentIDFilter(InputFilter):
    parameter_name = 'assignment_id'
    title = _('Assignment ID')

    def queryset(self, request, queryset):
        try:
            if self.value() is not None:
                _id = self.value()
                return queryset.filter(assignment_id=_id)
        except ValueError:
            self.model_admin.message_user(
                request, 'Search value should only be number/integer.', messages.WARNING)


class UserIDFilter(InputFilter):
    parameter_name = 'user_id'
    title = _('User ID')

    def queryset(self, request, queryset):
        try:
            if self.value() is not None:
                _id = self.value()
                return queryset.filter(user_id=_id)
        except ValueError:
            self.model_admin.message_user(
                request, 'Search value should only be number/integer.', messages.WARNING)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "id_number", "problem_name",
                    "attempt_number", "assignment_id", "user_id")
    list_filter = [AssignmentIDFilter, UserIDFilter]
    actions = [AdminActions.submission_regrade]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Token, TokenAdmin)
