from django.urls import path
from .views import (ListCreateMortgageAPIView, ListCreateRealEstateObjectAPIView, ListCreatePaymentAPIView,
                    RetrieveUpdateDestroyMortgageAPIView, RetrieveUpdateDestroyRealEstateObjectAPIView,
                    RetrieveUpdateDestroyPaymentAPIView)


urlpatterns = [
    path('mortgage/', ListCreateMortgageAPIView.as_view(), name='get_post_mortgages'),
    path('mortgage/<int:pk>/', RetrieveUpdateDestroyMortgageAPIView.as_view(), name='get_delete_update_mortgage'),
    path('real-estate-obj/', ListCreateRealEstateObjectAPIView.as_view(), name='get_post_real_estate_objects'),
    path('real-estate-obj/<int:pk>/', RetrieveUpdateDestroyRealEstateObjectAPIView.as_view(),
         name='get_delete_update_real_estate_object'),
    path('payment/', ListCreatePaymentAPIView.as_view(), name='get_post_payments'),
    path('payment/<int:pk>/', RetrieveUpdateDestroyPaymentAPIView.as_view(), name='get_delete_update_payment'),
]
