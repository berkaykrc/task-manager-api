from django.contrib import admin
from tasks.admin import TaskInline

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'owner')
    list_filter = ('start_date', 'end_date')
    search_fields = ['name', 'description']
    inlines = [TaskInline]  # Add this line
    filter_horizontal = ('users',)


admin.site.register(Project, ProjectAdmin)
