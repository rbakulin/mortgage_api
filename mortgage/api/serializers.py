from rest_framework import serializers
from mortgage.models import Mortgage, RealEstateObject, Payment


class RealEstateObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateObject
        fields = ['id', 'price', 'area', 'address', 'built_year']


class MortgageSerializer(serializers.ModelSerializer):
    real_estate_object_id = serializers.PrimaryKeyRelatedField(many=False, queryset=RealEstateObject.objects.all())
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Mortgage
        fields = ['id', 'percent', 'period', 'first_payment_amount', 'total_amount', 'issue_date',
                  'real_estate_object_id', 'user_id']


class PaymentSerializer(serializers.ModelSerializer):
    mortgage_id = serializers.PrimaryKeyRelatedField(many=False, queryset=Mortgage.objects.all())

    class Meta:
        model = Payment
        fields = ['id', 'date', 'amount', 'bank_share', 'debt_decrease', 'debt_rest', 'mortgage_id']
