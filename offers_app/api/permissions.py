from rest_framework.permissions import BasePermission

class IsProviderOrReadOnly(BasePermission):
    """Erlaubt nur Anbietern die Erstellung von Angeboten"""
    def has_permission(self, request, view):
        # Authentifizierte Benutzer können Angebote erstellen
        if request.method == 'POST':
            return request.user.is_authenticated
        # Alle anderen Methoden sind erlaubt
        return True

class IsOwnerOrAdmin(BasePermission):
    """Erlaubt nur Besitzern oder Admins Änderungen"""
    def has_object_permission(self, request, view, obj):
        # Leseberechtigungen für alle
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        # Schreibberechtigungen nur für Besitzer oder Admins
        return obj.user == request.user or request.user.is_superuser

class OfferPermission(IsProviderOrReadOnly, IsOwnerOrAdmin):
    """Kombinierte Berechtigungen für Angebote"""
    pass

class OfferDetailPermission(IsOwnerOrAdmin):
    """Berechtigungen für Angebotsdetails"""
    def has_object_permission(self, request, view, obj):
        # Zugriff auf das übergeordnete Offer-Objekt
        return super().has_object_permission(request, view, obj.offer)