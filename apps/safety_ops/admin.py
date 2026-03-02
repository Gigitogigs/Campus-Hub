from django.contrib import admin
from .models import Report

# Register your models here.
@admin.action(description='Mark selected reports as Resolved')
def make_resolved(modeladmin, request, queryset):
    queryset.update(status='RESOLVED')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_reporter', 'content_type', 'object_id', 'reason', 'status', 'created_at', 'is_anonymous')
    list_filter = ('status', 'reason', 'is_anonymous', 'created_at', 'content_type')
    search_fields = ('description', 'object_id', 'reporter__email')
    actions = [make_resolved]
    readonly_fields = ('created_at', 'updated_at')

    def get_reporter(self, obj):
        if obj.is_anonymous:
            return "Anonymous (Hidden)"
        return obj.reporter.email if obj.reporter else "Deleted User"
    get_reporter.short_description = 'Reporter'

admin.site.register(Report, ReportAdmin)
