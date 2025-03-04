from rest_framework.permissions import BasePermission

class CustomerPermission(BasePermission):
    """
    Allows only users with the type "customer" to create new resources.
    This permission only applies to POST requests; all other methods are allowed.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        return bool(
            hasattr(request.user, 'profile') and
            request.user.profile.type == 'customer'
        )


class OrderPermission(BasePermission):
    """
    Permission for Order objects.
    
    - DELETE: Only superusers.
    - PATCH: Only users with a business profile.
    - Other methods: Allowed if the user's ID matches the order's business_user.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_superuser
        if request.method == 'PATCH':
            profile = getattr(request.user, 'profile', None)
            return profile is not None and profile.type == 'business'
        return request.user.id == obj.business_user
        
        
class IsReviewerOrAdmin(BasePermission):
    """
    Allows access only to the review's creator (reviewer) or an admin.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.reviewer or request.user.is_superuser