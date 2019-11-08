from rest_framework.permissions import BasePermission

from app.models import Token


class TokenPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_X_TOKEN')
        if not token:
            return False

        token = Token.objects.filter(token=token)
        return token.count() == 1
