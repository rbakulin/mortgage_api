from datetime import datetime

from rest_framework import status
from rest_framework.generics import (ListAPIView, ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mortgage.models import Mortgage, Payment

from .pagination import CustomPagination
from .payment_schedule import PaymentScheduler
from .permissions import IsOwner
from .serializers import (BasicPaymentSerializer, MortgageSerializer,
                          PaymentSerializer)


# MORTGAGE
class ListCreateMortgageAPIView(ListCreateAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Mortgage.objects.filter(user=self.request.user)


class RetrieveUpdateDestroyMortgageAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsOwner, IsAuthenticated]

    def update(self, request, *args, **kwargs):
        response = super().update(request, partial=True, *args, **kwargs)
        # should update payment schedule after updating mortgage itself
        current_mortgage = Mortgage.get_mortgage(kwargs['pk'])
        current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        current_payments.delete()  # delete old payment schedule if it exists
        payment_scheduler = PaymentScheduler(mortgage=current_mortgage)
        payment_scheduler.calc_and_save_payments_schedule()

        return response


# PAYMENT
class ListPaymentAPIView(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        current_payments = Payment.objects.filter(mortgage_id=self.kwargs['mortgage_id']).order_by('date', 'created_at')
        return current_payments

    def get(self, request, *args, **kwargs):
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': Mortgage.get_not_found_error_message()},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': Mortgage.get_not_belong_error_message()},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().get(request, *args, **kwargs)
        return response


class CalcPaymentsSchedule(ListCreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        current_payments = Payment.objects.filter(mortgage_id=self.kwargs['mortgage_id']).order_by('date', 'created_at')
        return current_payments

    def post(self, request, *args, **kwargs):
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': Mortgage.get_not_found_error_message()},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': Mortgage.get_not_belong_error_message()},
                            status=status.HTTP_403_FORBIDDEN)

        current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        current_payments.delete()  # delete old payment schedule if it exists

        payment_scheduler = PaymentScheduler(mortgage=current_mortgage)
        payment_scheduler.calc_and_save_payments_schedule()
        response = super().get(request, *args, **kwargs)
        return response


class AddExtraPayment(ListCreateAPIView):
    serializer_class = BasicPaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        current_payments = Payment.objects.filter(mortgage_id=self.kwargs['mortgage_id']).order_by('date', 'created_at')
        return current_payments

    def post(self, request, *args, **kwargs):
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': Mortgage.get_not_found_error_message()},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': Mortgage.get_not_belong_error_message()},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        extra_payment = Payment(
            mortgage=current_mortgage,
            amount=request.data['amount'],
            date=datetime.strptime(request.data['date'], '%Y-%m-%d').date(),
            is_extra=True
        )
        payment_scheduler = PaymentScheduler(mortgage=current_mortgage, extra_payment=extra_payment)
        payment_scheduler.save_extra_payment()

        self.serializer_class = PaymentSerializer
        response = super().get(request, *args, **kwargs)
        return response
