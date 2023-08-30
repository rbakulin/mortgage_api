from typing import Any, Callable

from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from mortgage.messages import responses
from mortgage.models import Mortgage, Payment
from mortgage.payment_schedule import PaymentScheduler


def check_mortgage_permissions(
        mortgage_id: int, user_id: int, http_method: Callable, request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    current_mortgage = Mortgage.get_mortgage(mortgage_id)
    if not current_mortgage:
        return Response(data={'detail': responses.MORTGAGE_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    if current_mortgage.user.pk != user_id:
        return Response(data={'detail': responses.MORTGAGE_NOT_BELONG},
                        status=status.HTTP_403_FORBIDDEN)
    return http_method(request, *args, **kwargs)


def update_payment_schedule(mortgage_id: int) -> None:
    current_mortgage = Mortgage.get_mortgage(mortgage_id)
    if not current_mortgage:
        return
    current_payments = Payment.objects.filter(mortgage_id=current_mortgage.pk)
    if not current_payments:
        return
    current_payments.delete()  # delete old payment schedule if it exists
    payment_scheduler = PaymentScheduler(mortgage=current_mortgage)
    payment_scheduler.calc_and_save_payments_schedule()
