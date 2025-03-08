from rest_framework.permissions import BasePermission, SAFE_METHODS
from user_auth_app.models import UserProfile

class IsProviderOrReadOnly(BasePermission):
    """
    Allows only authenticated business users to create offers.
    All requests require authentication.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                return False
            return profile.type == UserProfile.UserType.BUSINESS
        return True

class IsOwnerOrAdmin(BasePermission):
    """
    Allows only owners or admins to modify objects.
    All requests require authentication.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_superuser or (hasattr(obj, 'user') and obj.user == request.user)

class OfferPermission(IsProviderOrReadOnly, IsOwnerOrAdmin):
    """Combined permissions for offers, enforcing provider and owner/admin rules."""
    pass

class OfferDetailPermission(IsOwnerOrAdmin):
    """Permissions for offer details, inheriting from IsOwnerOrAdmin but checking the parent offer."""
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.offer)