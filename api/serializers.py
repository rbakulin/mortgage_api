from rest_framework import serializers
from mortgage.models import Mortgage, RealEstateObject, Payment


class MortgageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mortgage
        fields = ['id', 'percent', 'period', 'first_payment_amount', 'total_amount', 'issue_date', 'real_estate_object']


class RealEstateObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateObject
        fields = ['id', 'price', 'area', 'address', 'built_year']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'date', 'amount', 'bank_percent', 'debt_decrease', 'debt_rest', 'mortgage']
