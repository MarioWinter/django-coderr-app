from rest_framework import permissions

class CustomerPermission(permissions.BasePermission):
    """
    Allows only users with the type "customer" to create new resources.
    This permission only applies to POST requests; all other methods are allowed.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        return bool(
            request.user and 
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.type == 'customer'
        )
