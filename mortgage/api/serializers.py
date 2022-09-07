from rest_framework import serializers

from mortgage.models import Mortgage, Payment


class MortgageSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Mortgage
        fields = ('id', 'percent', 'period', 'first_payment_amount', 'apartment_price', 'total_amount', 'issue_date',
                  'user_id')


class PaymentSerializer(serializers.ModelSerializer):
    mortgage_id = serializers.PrimaryKeyRelatedField(many=False, queryset=Mortgage.objects.all())

    class Meta:
        model = Payment
        fields = ('id', 'date', 'amount', 'bank_amount', 'debt_decrease', 'debt_rest', 'mortgage_id')


class BasicPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('date', 'amount')
