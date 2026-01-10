from rest_framework.permissions import BasePermission, SAFE_METHODS
from test_app.models import Role


class IsModeratorOrAdmin(BasePermission):
    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return request.user.role in [Role.moderator.name, Role.admin.name]


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.admin.name