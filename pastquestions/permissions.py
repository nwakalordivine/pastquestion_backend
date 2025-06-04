from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to allow only admin users to perform certain actions.
    """

    def has_permission(self, request, view):
        # Allow other methods only for admin users
        return request.user.is_authenticated and request.user.is_admin