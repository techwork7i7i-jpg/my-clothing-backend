"""
Account-level permissions (mostly public endpoints use AllowAny).
"""
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Example reusable permission: object must belong to request.user.
    Used by the files app for uploads; kept here as a shared pattern.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return getattr(obj, "user_id", None) == request.user.id
        return getattr(obj, "user", None) == request.user
