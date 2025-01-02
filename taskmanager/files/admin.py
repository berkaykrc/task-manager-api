from django.contrib import admin

from .models import SharedFile

admin.site.register(SharedFile)


class SharedFilesInline(admin.TabularInline):
    """Inline class for displaying tasks in the Project admin view."""

    model = SharedFile
    extra = 0
