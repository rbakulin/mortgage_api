from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from mortgage.models import Mortgage, Payment
from .serializers import BasicPaymentSerializer, MortgageSerializer, PaymentSerializer
from .permissions import IsOwner
from .pagination import CustomPagination
from .payment_schedule import PaymentScheduler


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


# PAYMENT
class ListCreatePaymentAPIView(ListCreateMortgageAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


class RetrieveUpdateDestroyPaymentAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class CalcPaymentsSchedule(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'error': Mortgage.get_not_found_error_message(mortgage_id)},
                            status=status.HTTP_404_NOT_FOUND)

        current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        current_payments.delete()  # delete old payment schedule if it exists

        payment_scheduler = PaymentScheduler(mortgage=current_mortgage)
        payment_scheduler.calc_and_save_payments_schedule()
        serializer = PaymentSerializer(current_payments, many=True)
        return Response(data=serializer.data)


class AddExtraPayment(ListAPIView):
    serializer_class = BasicPaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'error': Mortgage.get_not_found_error_message(mortgage_id)},
                            status=status.HTTP_404_NOT_FOUND)
        current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)

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

        serializer = PaymentSerializer(current_payments, many=True)
        return Response(data=serializer.data)
