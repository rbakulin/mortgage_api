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

from mortgage.messages import responses
from mortgage.models import Mortgage, Payment
from mortgage.payment_schedule import ExtraPaymentCalculator

from .helpers import check_mortgage_permissions, update_payment_schedule
from .pagination import PaymentPagination
from .permissions import IsOwner
from .serializers import (BasicPaymentSerializer, MortgageSerializer,
                          PaymentSerializer)


# MORTGAGE
class ListCreateMortgageAPIView(ListCreateAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    def get_queryset(self) -> QuerySet:
        return Mortgage.objects.filter(user=self.request.user)


class RetrieveUpdateDestroyMortgageAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsOwner, IsAuthenticated]

    def patch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = check_mortgage_permissions(
            *args, user_id=request.user.pk, http_method=super().patch, request=request, **kwargs
        )
        if not status.is_success(response.status_code):
            return response
        update_payment_schedule(kwargs['pk'])  # should update payment schedule after updating mortgage itself
        return response

    def put(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = check_mortgage_permissions(
            *args, user_id=request.user.pk, http_method=super().put, request=request, **kwargs
        )
        if not status.is_success(response.status_code):
            return response
        update_payment_schedule(kwargs['pk'])  # should update payment schedule after updating mortgage itself
        return response


# PAYMENT
class ListPaymentAPIView(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PaymentPagination
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
        response = check_mortgage_permissions(
            *args, user_id=request.user.pk, http_method=super().get, request=request, **kwargs
        )
        return response


class CalcPaymentsSchedule(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        success_response = {'code': status.HTTP_200_OK, 'data': {'detail': responses.CALCULATED_SUCCESSFULLY}}
        response = check_mortgage_permissions(
            *args, user_id=request.user.pk, success_response=success_response, request=request, **kwargs
        )
        if not status.is_success(response.status_code):
            return response
        update_payment_schedule(kwargs['mortgage_id'])
        return response


class AddExtraPayment(CreateAPIView):
    serializer_class = BasicPaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = check_mortgage_permissions(
            *args, user_id=request.user.pk, success_response={'code': status.HTTP_201_CREATED, 'data': request.data},
            request=request, **kwargs
        )
        if not status.is_success(response.status_code):
            return response

        data_to_validate = request.data | {'is_extra': True, 'mortgage_id': kwargs['mortgage_id']}
        serializer = self.serializer_class(data=data_to_validate)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        extra_payment_calculator = ExtraPaymentCalculator(payment_params=data_to_validate)
        extra_payment_calculator.save_extra_payment()
        return response
