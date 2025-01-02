"""
Profile model is registered with the Django admin site so that it can be managed from admin site.
"""

from django.contrib import admin

from .models import Profile

admin.site.register(Profile)
