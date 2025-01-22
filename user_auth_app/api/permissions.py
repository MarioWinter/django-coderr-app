from rest_framework.permissions import BasePermission

class ProfilePermission(BasePermission):
        
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE'  or request.method == 'PUT' or request.method == 'POST':
            return request.user.is_superuser
        return request.user == obj.user