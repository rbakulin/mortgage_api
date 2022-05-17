from django.urls import path
from .views import (ListCreateMortgageAPIView, ListCreatePaymentAPIView,
                    RetrieveUpdateDestroyMortgageAPIView,
                    RetrieveUpdateDestroyPaymentAPIView, CalcPaymentsSchedule)


urlpatterns = [
    path('mortgage/', ListCreateMortgageAPIView.as_view(), name='get_post_mortgages'),
    path('mortgage/<int:pk>/', RetrieveUpdateDestroyMortgageAPIView.as_view(), name='get_delete_update_mortgage'),
    path('payment/', ListCreatePaymentAPIView.as_view(), name='get_post_payments'),
    path('payment/<int:pk>/', RetrieveUpdateDestroyPaymentAPIView.as_view(), name='get_delete_update_payment'),
    path('calc-payment-schedule/<int:mortgage_id>/', CalcPaymentsSchedule.as_view(), name='calc_payment_schedule'),
]
