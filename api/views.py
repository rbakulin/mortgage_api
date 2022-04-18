from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from mortgage.models import Mortgage, RealEstateObject, Payment
from .serializers import MortgageSerializer, RealEstateObjectSerializer, PaymentSerializer
from .pagination import CustomPagination


class ListCreateMortgageAPIView(ListCreateAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


class RetrieveUpdateDestroyMortgageAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    # permission_classes = [IsAuthenticated]


class ListCreateRealEstateObjectAPIView(ListCreateMortgageAPIView):
    serializer_class = RealEstateObjectSerializer
    queryset = RealEstateObject.objects.all()
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


class RetrieveUpdateDestroyRealEstateObjectAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = RealEstateObjectSerializer
    queryset = RealEstateObject.objects.all()
    # permission_classes = [IsAuthenticated]


class ListCreatePaymentAPIView(ListCreateMortgageAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


class RetrieveUpdateDestroyPaymentAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    # permission_classes = [IsAuthenticated]
