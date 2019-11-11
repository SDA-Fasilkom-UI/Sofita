from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

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


# https://medium.com/@hakibenita/how-to-add-a-text-filter-to-django-admin-5d1db93772d8
class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" opstion.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class TextFilter(InputFilter):
    parameter_name = 'ID'
    title = _('Assignment ID or User ID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            uid = self.value()
            return queryset.filter(
                Q(assignment_id=uid) |
                Q(user_id=uid)
            )


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id_number", "problem_name",
                    "attempt_number", "assignment_id", "user_id")
    list_filter = [TextFilter]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Token, TokenAdmin)
