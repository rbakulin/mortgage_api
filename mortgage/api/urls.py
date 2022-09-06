from django.urls import path
from .views import (ListCreateMortgageAPIView, ListPaymentAPIView,
                    RetrieveUpdateDestroyMortgageAPIView, CalcPaymentsSchedule, AddExtraPayment)


urlpatterns = [
    path('mortgage/', ListCreateMortgageAPIView.as_view(), name='get_post_mortgages'),
    path('mortgage/<int:pk>/', RetrieveUpdateDestroyMortgageAPIView.as_view(), name='get_delete_update_mortgage'),
    path('mortgage/<int:mortgage_id>/payment/', ListPaymentAPIView.as_view(), name='get_payments_for_mortgage'),
    path('calc-payment-schedule/<int:mortgage_id>/', CalcPaymentsSchedule.as_view(), name='calc_payment_schedule'),
    path('add-extra-payment/<int:mortgage_id>/', AddExtraPayment.as_view(), name='add_extra_payment'),
]
