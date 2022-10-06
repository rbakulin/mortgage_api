from datetime import datetime
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from mortgage import response_messages
from mortgage.models import Mortgage, Payment

from .pagination import CustomPagination
from .payment_schedule import ExtraPaymentCalculator, PaymentScheduler
from .permissions import IsOwner
from .serializers import (BasicPaymentSerializer, MortgageSerializer,
                          PaymentSerializer)


# MORTGAGE
class ListCreateMortgageAPIView(ListCreateAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    def get_queryset(self) -> QuerySet:
        return Mortgage.objects.filter(user=self.request.user)


class RetrieveUpdateDestroyMortgageAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsOwner, IsAuthenticated]

    def patch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        current_mortgage = Mortgage.get_mortgage(kwargs['pk'])
        if not current_mortgage:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_BELONG},
                            status=status.HTTP_403_FORBIDDEN)
        response = super().patch(request, *args, **kwargs)
        current_mortgage_upd = Mortgage.get_mortgage(kwargs['pk'])

        # TODO: redundant condition, type hints fix
        if current_mortgage_upd:
            # should update payment schedule after updating mortgage itself
            current_payments = Payment.objects.filter(mortgage_id=current_mortgage_upd.pk)
            current_payments.delete()  # delete old payment schedule if it exists
            payment_scheduler = PaymentScheduler(mortgage=current_mortgage_upd)
            payment_scheduler.calc_and_save_payments_schedule()

        return response

    # TODO: DRY
    def put(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        current_mortgage = Mortgage.get_mortgage(kwargs['pk'])
        if not current_mortgage:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_BELONG},
                            status=status.HTTP_403_FORBIDDEN)
        response = super().put(request, *args, **kwargs)
        current_mortgage_upd = Mortgage.get_mortgage(kwargs['pk'])

        # TODO: redundant condition, type hints fix
        if current_mortgage_upd:
            # should update payment schedule after updating mortgage itself
            current_payments = Payment.objects.filter(mortgage_id=current_mortgage_upd.pk)
            current_payments.delete()  # delete old payment schedule if it exists
            payment_scheduler = PaymentScheduler(mortgage=current_mortgage_upd)
            payment_scheduler.calc_and_save_payments_schedule()

        return response


# PAYMENT
class ListPaymentAPIView(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    is_extra = openapi.Parameter('is_extra', openapi.IN_QUERY,
                                 description="Get only extra payments",
                                 type=openapi.TYPE_BOOLEAN)

    def get_queryset(self) -> QuerySet:
        queryset = Payment.objects.filter(mortgage_id=self.kwargs['mortgage_id']).order_by('date', 'created_at')
        is_extra = self.request.query_params.get('is_extra')
        if is_extra and is_extra.lower() in ('1', 'true'):
            queryset = Payment.objects.filter(
                mortgage_id=self.kwargs['mortgage_id'], is_extra=True).order_by('date', 'created_at')
        return queryset

    @swagger_auto_schema(manual_parameters=[is_extra])
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_BELONG},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().get(request, *args, **kwargs)
        return response


class CalcPaymentsSchedule(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_BELONG},
                            status=status.HTTP_403_FORBIDDEN)

        current_payments = Payment.objects.filter(mortgage_id=current_mortgage.id)
        current_payments.delete()  # delete old payment schedule if it exists

        payment_scheduler = PaymentScheduler(mortgage=current_mortgage)
        payment_scheduler.calc_and_save_payments_schedule()
        return Response(data={'detail': response_messages.CALCULATED_SUCCESSFULLY},
                        status=status.HTTP_200_OK)


class AddExtraPayment(CreateAPIView):
    serializer_class = BasicPaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        mortgage_id = kwargs['mortgage_id']
        current_mortgage = Mortgage.get_mortgage(mortgage_id)
        if not current_mortgage:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
        if current_mortgage.user != request.user:
            return Response(data={'detail': response_messages.MORTGAGE_NOT_BELONG},
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
        if not current_mortgage.first_payment_date < extra_payment.date < current_mortgage.last_payment_date:
            return Response(data={'detail': response_messages.PAYMENT_DATE_INCORRECT},
                            status=status.HTTP_400_BAD_REQUEST)

        prev_extra_payment = extra_payment.get_prev_payment()
        if extra_payment.amount > prev_extra_payment.debt_rest:
            return Response(data={'detail': response_messages.PAYMENT_AMOUNT_INCORRECT},
                            status=status.HTTP_400_BAD_REQUEST)

        extra_payment_calculator = ExtraPaymentCalculator(mortgage=current_mortgage, extra_payment=extra_payment)
        extra_payment_calculator.save_extra_payment()

        return Response(data={'detail': response_messages.PAYMENT_ADDED_SUCCESSFULLY},
                        status=status.HTTP_200_OK)
