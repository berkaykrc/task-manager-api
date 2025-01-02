"""
This module contains the admin configuration for the Project model.
"""

from django.contrib import admin
from files.admin import SharedFilesInline
from tasks.admin import TaskInline

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Project model.

    This class defines the display, filtering, search, and inline editing options for the Project model in the Django admin interface.

    Attributes:
        list_display (tuple): A tuple of field names to be displayed in the admin list view.
        list_filter (tuple): A tuple of field names to be used for filtering in the admin list view.
        search_fields (list): A list of field names to be used for searching in the admin list view.
        inlines (list): A list of inline models to be displayed and edited on the Project admin page.
        filter_horizontal (tuple): A tuple of field names to be displayed as horizontal filter widgets in the admin interface.

    """

    list_display = ("name", "description", "start_date", "end_date", "owner")
    list_filter = ("start_date", "end_date")
    search_fields = ["name", "description"]
    inlines = [TaskInline, SharedFilesInline]
    filter_horizontal = ("users",)


admin.site.register(Project, ProjectAdmin)
