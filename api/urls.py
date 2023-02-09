from django.urls import path

from .views import (AddExtraPayment, CalcPaymentsSchedule,
                    ListCreateMortgageAPIView, ListPaymentAPIView,
                    RetrieveUpdateDestroyMortgageAPIView)

urlpatterns = [
    path('mortgage/', ListCreateMortgageAPIView.as_view(), name='get_post_mortgages'),
    path('mortgage/<int:pk>/', RetrieveUpdateDestroyMortgageAPIView.as_view(), name='get_delete_update_mortgage'),
    path('mortgage/<int:mortgage_id>/payment/', ListPaymentAPIView.as_view(), name='get_payments_for_mortgage'),
    path('mortgage/<int:mortgage_id>/calc-payment-schedule/', CalcPaymentsSchedule.as_view(),
         name='calc_payment_schedule'),
    path('mortgage/<int:mortgage_id>/add-extra-payment/', AddExtraPayment.as_view(), name='add_extra_payment'),
]
