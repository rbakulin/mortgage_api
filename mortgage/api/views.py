from math import pow
from decimal import Decimal
from dateutil import relativedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from mortgage.models import Mortgage, Payment
from .serializers import MortgageSerializer, PaymentSerializer
from .permissions import IsOwner
from .pagination import CustomPagination


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

    def get(self, request, *args, **kwargs):
        try:
            current_mortgage = Mortgage.objects.get(pk=kwargs['mortgage_id'])
        except Mortgage.DoesNotExist:
            return Response(data={'error': 'Mortgage does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        except Payment.DoesNotExist:
            pass
        else:
            # delete old payment schedule if it exists
            current_payments.delete()

        period_in_months = current_mortgage.period * 12
        dem = Decimal(current_mortgage.percent / 1200 + 1)
        power = Decimal(pow(dem, period_in_months))
        coef = Decimal(power * (dem - 1) / (power - 1))

        amount = round(coef * current_mortgage.total_amount, 2)

        for i in range(1, period_in_months + 1):
            payment = Payment()
            payment.mortgage = current_mortgage
            payment.amount = amount
            payment.date = current_mortgage.issue_date + relativedelta.relativedelta(months=i)
            payment.bank_share = payment.calc_bank_share()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
            payment.save()

        serializer = PaymentSerializer(current_payments, many=True)
        return Response(data=serializer.data)
