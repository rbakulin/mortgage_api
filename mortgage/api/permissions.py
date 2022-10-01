from typing import Any, Callable

from django.http import HttpRequest
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request: HttpRequest, view: Callable, obj: Any) -> bool:
        return obj.user == request.user
