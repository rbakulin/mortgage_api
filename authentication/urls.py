from django.urls import path

from authentication.views import (RegisterView,
                                  TokenObtainPairViewSwaggerFixed,
                                  TokenRefreshViewSwaggerFixed)

urlpatterns = [
    path('token/', TokenObtainPairViewSwaggerFixed.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshViewSwaggerFixed.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
]
