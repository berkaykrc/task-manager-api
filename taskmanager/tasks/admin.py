from re import T
from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'duration', 'status', 'priority', 'creator', 'display_assigned')
    list_filter = ('status', 'priority', 'creator')
    search_fields = ('name', 'description')
    ordering = ('-start_date',)

    def display_assigned(self, obj):
        return ", ".join([assigned.username for assigned in obj.assigned.all()])
    display_assigned.short_description = 'Assigned To'

admin.site.register(Task,TaskAdmin)