from rest_framework.permissions import BasePermission

class OfferDetailPermission(BasePermission):
        
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method != 'GET':
            return request.user.is_superuser
        return request.user == obj.user

class OfferPermission(BasePermission):
        
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            return request.user.is_superuser
        return request.user == obj.user