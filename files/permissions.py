"""
File access: only the owner may view, list, or delete their uploads.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuthenticatedOwner(IsAuthenticated):
    """User must be logged in (inherited from IsAuthenticated)."""

    def has_permission(self, request, view):
        return super().has_permission(request, view)


class IsFileOwner(BasePermission):
    """Object-level: uploaded file must belong to request.user."""

    message = "You do not have permission to access this file."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
