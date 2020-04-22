from django.contrib import admin, messages

from app.constants import K_REDIS_MIDDLE_PRIORITY
from grader import tasks
from grader.models import Submission


class SubmissionAdminActions():
    """
    Container for functions/actions that need to be used by other SubmissionAdmin
    """

    @staticmethod
    def regrade_submissions(modeladmin, request, queryset):
        queryset.update(status=Submission.PENDING)
        for submission in queryset.all():
            tasks.grade.apply_async((submission.id, submission.assignment_id,
                                     submission.user_id, submission.attempt_number),
                                    priority=K_REDIS_MIDDLE_PRIORITY)

        modeladmin.message_user(
            request, "Selected submission will be regraded")


class InputFilter(admin.SimpleListFilter):
    """
    https://medium.com/@hakibenita/how-to-add-a-text-filter-to-django-admin-5d1db93772d8
    """
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
            (k, v) for k, v in changelist.get_filters_params().items() if k != self.parameter_name
        )
        yield all_choice


class AssignmentIDFilter(InputFilter):
    parameter_name = 'assignment_id'
    title = 'Assignment ID'

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
    title = 'User ID'

    def queryset(self, request, queryset):
        try:
            if self.value() is not None:
                _id = self.value()
                return queryset.filter(user_id=_id)
        except ValueError:
            self.model_admin.message_user(
                request, 'Search value should only be number/integer.', messages.WARNING)


class IDNumberFilter(InputFilter):
    parameter_name = 'id_number'
    title = 'ID Number'

    def queryset(self, request, queryset):
        try:
            if self.value() is not None:
                _id = self.value()
                return queryset.filter(id_number=_id)
        except ValueError:
            self.model_admin.message_user(
                request, 'Search value should only be number/integer.', messages.WARNING)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "id_number", "problem_name", "attempt_number",
                    "formatted_time_modified", "assignment_id", "user_id", "grade", "status")
    readonly_fields = ("grade", "status", "assignment_id", "course_id", "activity_id", "user_id",
                       "id_number", "attempt_number", "due_date", "cut_off_date", "time_modified")
    list_filter = [AssignmentIDFilter, UserIDFilter, IDNumberFilter]
    actions = [SubmissionAdminActions.regrade_submissions]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Submission, SubmissionAdmin)
