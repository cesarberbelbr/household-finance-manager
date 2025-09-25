from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Defines the admin interface for the CustomUser model.
    """
    model = CustomUser
    # You can customize list_display, fieldsets, etc., here
    # For now, we'll use the defaults from UserAdmin.

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)