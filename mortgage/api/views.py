from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from mortgage.models import Mortgage, Payment
from .serializers import MortgageSerializer, PaymentSerializer
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

    # TODO: replace it with POST (REST)
    def get(self, request, *args, **kwargs):
        # TODO: DRY try/except
        try:
            current_mortgage = Mortgage.objects.get(pk=kwargs['mortgage_id'])
        except Mortgage.DoesNotExist:
            return Response(data={'error': f'Mortgage with id {kwargs["mortgage_id"]} does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        except Payment.DoesNotExist:
            current_payments = Payment.objects.none()
        else:
            # delete old payment schedule if it exists
            current_payments.delete()

        payment_scheduler = PaymentScheduler(current_mortgage)
        payment_scheduler.calc_and_save_payments_schedule()
        serializer = PaymentSerializer(current_payments, many=True)
        return Response(data=serializer.data)


class AddExtraPayment(ListAPIView):  # TODO: is list view the most suitable?
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        try:
            current_mortgage = Mortgage.objects.get(pk=kwargs['mortgage_id'])
        except Mortgage.DoesNotExist:
            return Response(data={'error': f'Mortgage with id {kwargs["mortgage_id"]} does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        except Payment.DoesNotExist:
            current_payments = Payment.objects.none()

        extra_payment = Payment(
            mortgage=current_mortgage,
            amount=request.data['amount'],
            date=datetime.strptime(request.data['date'], '%Y-%m-%d').date(),
            is_extra=True
        )
        payment_scheduler = PaymentScheduler(current_mortgage, extra_payment)
        payment_scheduler.save_extra_payment()

        serializer = PaymentSerializer(current_payments, many=True)
        return Response(data=serializer.data)
