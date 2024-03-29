import io
import os
import zipfile

from django import forms
from django.contrib import admin, messages
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse

from app.constants import K_REDIS_LOW_PRIORITY
from grader import tasks
from grader.models import Submission


def check_selected_submission(modeladmin, request, queryset):
    assignment_ids = queryset.\
        order_by("assignment_id").\
        values_list("assignment_id", flat=True).\
        distinct()

    if len(assignment_ids) > 1:
        modeladmin.message_user(
            request,
            "Only one assignment ID allowed.",
            messages.ERROR
        )
        return False

    return True


class SubmissionAdminAction():

    @staticmethod
    def regrade_submissions(modeladmin, request, queryset):
        if not check_selected_submission(modeladmin, request, queryset):
            return

        queryset.update(status=Submission.PENDING)
        for sub in queryset.all():
            tasks.grade_submission.apply_async(
                (sub.id, sub.assignment_id, sub.course_id,
                 sub.activity_id, sub.user_id, sub.attempt_number),
                priority=K_REDIS_LOW_PRIORITY)

        modeladmin.message_user(
            request, "Selected submission will be regraded.")

    @staticmethod
    def download_submissions(modeladmin, request, queryset):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for sub in queryset.all():
                filepath = os.path.join(
                    str(sub.assignment_id),
                    sub.id_number,
                    str(sub.attempt_number) + "-" + str(sub.grade),
                    sub.filename)
                zip_file.writestr(filepath, sub.content)

        response = HttpResponse(zip_buffer.getvalue(),
                                content_type="application/zip")
        filename = "submissions-" + str(timezone.now().timestamp()) + ".zip"
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response


class TimeMemoryLimitAction():

    template = 'admin/time_memory_limit_form.html'

    class TimeMemoryLimitForm(forms.Form):
        time_limit = forms.IntegerField(min_value=1, max_value=5)
        memory_limit = forms.IntegerField(min_value=64, max_value=512)

    @classmethod
    def change_time_and_memory_limit(cls, modeladmin, request, queryset):
        if not check_selected_submission(modeladmin, request, queryset):
            return

        if 'do_action' in request.POST:
            form = cls.TimeMemoryLimitForm(request.POST)
            if form.is_valid():
                time_limit = form.cleaned_data["time_limit"]
                memory_limit = form.cleaned_data["memory_limit"]
                queryset.update(time_limit=time_limit,
                                memory_limit=memory_limit)

                modeladmin.message_user(
                    request, "Selected submission has been changed.")
                return

        else:
            form = cls.TimeMemoryLimitForm()

        return render(request, cls.template, {
            "title": "Change time and memory limit",
            "form": form,

            "action": request.POST.get("action"),
            "select_across": request.POST.get("select_across"),
            "index": request.POST.get("index"),
            "selected_action": request.POST.getlist("_selected_action"),
        })


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
                request, 'Search value should only be number/integer.',
                messages.WARNING)


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
                request, 'Search value should only be number/integer.',
                messages.WARNING)


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
                request, 'Search value should only be number/integer.',
                messages.WARNING)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("submission_id", "id_number", "problem_name",
                    "attempt_number", "time_submitted", "assignment_id",
                    "user_id", "grade", "status")
    readonly_fields = ("grade", "verdict", "status", "assignment_id",
                       "course_id", "activity_id", "user_id", "id_number",
                       "attempt_number", "due_date", "cut_off_date",
                       "time_modified")
    list_filter = [AssignmentIDFilter, UserIDFilter, IDNumberFilter]
    actions = [
        SubmissionAdminAction.regrade_submissions,
        TimeMemoryLimitAction.change_time_and_memory_limit,
        SubmissionAdminAction.download_submissions
    ]

    def submission_id(self, obj):
        return "Submission ({})".format(obj.id)
    submission_id.admin_order_field = "id"

    def time_submitted(self, obj):
        return obj.formatted_time_modified
    time_submitted.admin_order_field = "time_modified"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Submission, SubmissionAdmin)
