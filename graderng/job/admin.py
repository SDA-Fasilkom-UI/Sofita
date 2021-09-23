from django.contrib import admin

from grader.admin import AssignmentIDFilter
from job import tasks
from job.models import MossJob, ReportJob


class MossJobAdminActions():
    """
    Container for functions/actions that need to be used by other MossJobAdmin
    """

    @staticmethod
    def rerun_check(modeladmin, request, queryset):
        queryset.update(status=MossJob.PENDING)
        for moss_job in queryset.all():
            tasks.check_plagiarism.delay(moss_job.id)

        modeladmin.message_user(
            request, "Selected moss job will be rerun")


class MossJobAdmin(admin.ModelAdmin):

    list_display = ("moss_job", "assignment_id_list",
                    "name", "time_created", "zip_file")
    readonly_fields = ("zip_file", "log", "status",
                       "time_created", "id", "assignment_id")
    actions = [MossJobAdminActions.rerun_check]

    def moss_job(self, obj):
        return "Moss Job ({})".format(obj.id)

    moss_job.admin_order_field = "id"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            tasks.check_plagiarism.delay(obj.id)


class ReportJobAdminActions():
    """
    Container for functions/actions that need to be used by other ReportJobAdmin
    """

    @staticmethod
    def regenerate_report(modeladmin, request, queryset):
        queryset.update(status=ReportJob.PENDING)
        for report_job in queryset.all():
            tasks.generate_report.delay(report_job.id)

        modeladmin.message_user(
            request, "Selected report job will be rerun")


class ReportJobAdmin(admin.ModelAdmin):

    list_display = ("report_job", "assignment_id",
                    "name", "time_created", "csv_file")
    readonly_fields = ("csv_file", "log", "status",
                       "time_created", "id", "assignment_id")
    actions = [ReportJobAdminActions.regenerate_report]

    def report_job(self, obj):
        return "Report Job ({})".format(obj.id)

    report_job.admin_order_field = "id"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            tasks.generate_report.delay(obj.id)


admin.site.register(MossJob, MossJobAdmin)
admin.site.register(ReportJob, ReportJobAdmin)
