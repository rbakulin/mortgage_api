from django.urls import path
from .views import ListCreateMovieAPIView, RetrieveUpdateDestroyMovieAPIView


urlpatterns = [
    path('mortgage/', ListCreateMovieAPIView.as_view(), name='get_post_mortgages'),
    path('mortgage/<int:pk>/', RetrieveUpdateDestroyMovieAPIView.as_view(), name='get_delete_update_mortgage'),
]