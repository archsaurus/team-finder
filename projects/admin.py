from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'participants_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'owner__email']
    readonly_fields = ['created_at']

    filter_horizontal = ['participants']

    def participants_count(self, obj):
        return obj.participants.count()

    participants_count.short_description = 'Участников'
