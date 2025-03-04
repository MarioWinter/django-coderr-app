from rest_framework.permissions import BasePermission
from user_auth_app.models import UserProfile

class IsProviderOrReadOnly(BasePermission):
    """
    Allows only authenticated business users to create offers.
    Read access is granted to everyone.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return False
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                return False
            return profile.type == UserProfile.UserType.BUSINESS
        return True

class IsOwnerOrAdmin(BasePermission):
    """Allows only owners or admins to modify objects. Read access is granted to everyone."""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user or request.user.is_superuser

class OfferPermission(IsProviderOrReadOnly, IsOwnerOrAdmin):
    """Combined permissions for offers, enforcing provider and owner/admin rules."""
    pass

class OfferDetailPermission(IsOwnerOrAdmin):
    """Permissions for offer details, inheriting from IsOwnerOrAdmin but checking the parent offer."""
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.offer)