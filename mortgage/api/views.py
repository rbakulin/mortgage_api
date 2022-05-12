from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from mortgage.models import Mortgage, RealEstateObject, Payment
from .serializers import MortgageSerializer, RealEstateObjectSerializer, PaymentSerializer
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


class RetrieveUpdateDestroyMortgageAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MortgageSerializer
    queryset = Mortgage.objects.all()
    permission_classes = [IsOwner, IsAuthenticated]


# REAL ESTATE OBJECT
class ListCreateRealEstateObjectAPIView(ListCreateMortgageAPIView):
    serializer_class = RealEstateObjectSerializer
    queryset = RealEstateObject.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


class RetrieveUpdateDestroyRealEstateObjectAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = RealEstateObjectSerializer
    queryset = RealEstateObject.objects.all()
    permission_classes = [IsAuthenticated]


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
