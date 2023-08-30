from typing import Any

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .serializers import (RegisterSerializer, TokenObtainPairSuccessSerializer,
                          TokenRefreshSuccessSerializer,
                          UserCreateSuccessSerializer)


# For some reason yasg generates incorrect doc for token endpoints, so we have to inherit original views
# to use swagger_auto_schema decorator via witch we can redefine incorrect responses
class TokenObtainPairViewSwaggerFixed(TokenObtainPairView):
    @swagger_auto_schema(responses={200: TokenObtainPairSuccessSerializer()})
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        return response


class TokenRefreshViewSwaggerFixed(TokenRefreshView):
    @swagger_auto_schema(responses={200: TokenRefreshSuccessSerializer()})
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        return response


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(responses={201: UserCreateSuccessSerializer()})
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        return response
