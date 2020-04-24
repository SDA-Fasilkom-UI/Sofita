from django.contrib import admin

from grader.admin import AssignmentIDFilter
from moss import tasks
from moss.models import MossJob


class MossJobAdminActions():
    """
    Container for functions/actions that need to be used by other MossJobAdmin
    """

    @staticmethod
    def rerun_check(modeladmin, request, queryset):
        queryset.update(status=MossJob.PENDING)
        for moss_job in queryset.all():
            tasks.check_plagiarism.delay(moss_job._id)

        modeladmin.message_user(
            request, "Selected moss job will be rerun")


class MossJobAdmin(admin.ModelAdmin):

    list_display = ("__str__", "name", "zip_file")
    readonly_fields = ("zip_file", "log", "status", "time_created")
    list_filter = [AssignmentIDFilter]
    actions = [MossJobAdminActions.rerun_check]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            tasks.check_plagiarism.delay(obj._id)


admin.site.register(MossJob, MossJobAdmin)
