from rest_framework.permissions import BasePermission, SAFE_METHODS

class ProfilePermission(BasePermission):
    """
    Allows access to user profiles for authenticated users.
    Safe methods (GET, HEAD, OPTIONS) are allowed for any authenticated user.
    For unsafe methods (PATCH, PUT, DELETE, POST), only the profile owner or an admin is allowed.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.user or request.user.is_superuser