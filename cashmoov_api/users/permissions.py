from rest_framework.permissions import BasePermission
from cashmoov_api.users.models import User

class IsAdminUser(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs de type Admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == User.ADMIN
        )

class IsAssistantUser(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs de type Assistant.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == User.ASSISTANT
        )