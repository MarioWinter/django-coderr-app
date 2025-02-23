from django.contrib import admin
from user_auth_app.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    """
    list_display = ('user', 'type', 'location', 'tel', 'created_at')
    search_fields = ('user__username', 'location', 'tel')
    list_filter = ('type',)
    ordering = ('-created_at',)

admin.site.register(UserProfile, UserProfileAdmin)