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
    Custom permission class for controlling access to the Order model.
    Grants access to authenticated users.
    - For DELETE requests: Only superusers are allowed to delete the order.
    - For other requests: Users are allowed to perform actions on their own orders.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_superuser
        return request.user == obj.customer_user