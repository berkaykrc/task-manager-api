"""Admin module for Task app."""

from django.contrib import admin

from .models import Comment, Mention, Task


class CommentInline(admin.TabularInline):
    """Inline class for displaying comments in the Task admin view."""
    model = Comment
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    """
    Admin View for Task

    This class defines the admin interface for the Task model.
    It specifies the list display, list filter, search fields, and ordering options.
    It also defines a custom method to display the assigned users.

    Attributes:
        list_display (tuple): A tuple of field names to be displayed in the list view.
        list_filter (tuple): A tuple of field names to be used for filtering the list view.
        search_fields (tuple): A tuple of field names to be used for searching the list view.
        ordering (str): The field name to be used for ordering the list view.

    Methods:
        display_assigned(obj): Returns a string representation of the assigned users.

    """

    list_display = (
        "name",
        "start_date",
        "end_date",
        "duration",
        "status",
        "priority",
        "creator",
        "display_assigned",
    )
    list_filter = ("status", "priority", "creator")
    search_fields = ("name", "description")
    ordering = ("-start_date",)
    inlines = [CommentInline]

    def display_assigned(self, obj):
        """Display assigned to users."""
        return ", ".join([assigned.username for assigned in obj.assigned.all()])

    display_assigned.short_description = "Assigned To"


admin.site.register(Task, TaskAdmin)
admin.site.register(Comment)
admin.site.register(Mention)
