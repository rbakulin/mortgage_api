from rest_framework import serializers
from mortgage.models import Mortgage, RealEstateObject, Payment


class RealEstateObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateObject
        fields = ['id', 'price', 'area', 'address', 'built_year']


class MortgageSerializer(serializers.ModelSerializer):
    real_estate_object = RealEstateObjectSerializer(many=False)

    class Meta:
        model = Mortgage
        fields = ['id', 'percent', 'period', 'first_payment_amount', 'total_amount', 'issue_date']


class PaymentSerializer(serializers.ModelSerializer):
    mortgage = MortgageSerializer(many=False)

    class Meta:
        model = Payment
        fields = ['id', 'date', 'amount', 'bank_percent', 'debt_decrease', 'debt_rest']
