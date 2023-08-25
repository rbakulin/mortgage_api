from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from mortgage.messages import responses
from mortgage.models import Mortgage


def check_mortgage_permissions(mortgage_id: int, user_id: int) -> HttpResponse:
    current_mortgage = Mortgage.get_mortgage(mortgage_id)
    if not current_mortgage:
        return Response(data={'detail': responses.MORTGAGE_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    if current_mortgage.user.pk != user_id:
        return Response(data={'detail': responses.MORTGAGE_NOT_BELONG},
                        status=status.HTTP_403_FORBIDDEN)
    return Response(status=status.HTTP_200_OK)
