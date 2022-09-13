from typing import Any, Callable

from django.http import HttpRequest
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request: HttpRequest, view: Callable, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.creator == request.user


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request: HttpRequest, view: Callable, obj: Any) -> bool:
        return obj.user == request.user
