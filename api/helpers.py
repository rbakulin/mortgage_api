import logging
from typing import Any, Callable, Dict

from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from mortgage.messages import events, responses
from mortgage.models import Mortgage, Payment
from mortgage.payment_schedule import PaymentScheduler

logger = logging.getLogger('django')


def check_mortgage_permissions(
        *args: Any, user_id: int, http_method: Callable = None, success_response: Dict = None,
        request: HttpRequest, **kwargs: Any
) -> HttpResponse:
    mortgage_id = kwargs['mortgage_id'] if kwargs.get('mortgage_id') else kwargs['pk']
    current_mortgage = Mortgage.get_mortgage(mortgage_id)
    if not current_mortgage:
        return Response(data={'detail': responses.MORTGAGE_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    if current_mortgage.user.pk != user_id:
        return Response(data={'detail': responses.MORTGAGE_NOT_BELONG}, status=status.HTTP_403_FORBIDDEN)
    if not http_method:
        if not success_response:  # dumb check to fix typing hints
            raise Exception('One of http_method or success_response is required')
        return Response(data=success_response['data'], status=success_response['code'])
    return http_method(request, *args, **kwargs)


def update_payment_schedule(mortgage_id: int) -> None:
    current_payments = Payment.objects.filter(mortgage_id=mortgage_id)
    if not current_payments:
        return
    current_payments.delete()  # delete old payment schedule if it exists
    logger.info(events.SCHEDULE_DELETED.format(mortgage_id=mortgage_id))
    payment_scheduler = PaymentScheduler(mortgage_id=mortgage_id)
    payment_scheduler.calc_and_save_payments_schedule()
