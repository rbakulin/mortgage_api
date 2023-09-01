from typing import Dict

from rest_framework import serializers

from mortgage.helpers import parse_date
from mortgage.messages import responses
from mortgage.models import Mortgage, Payment


class MortgageSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Mortgage
        fields = ('id', 'percent', 'period', 'first_payment_amount', 'apartment_price', 'credit_amount', 'issue_date',
                  'user_id')


class BasicPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('date', 'amount')

    def validate(self, attrs: Dict) -> Dict:
        super().validate(attrs)
        if self.initial_data.get('is_extra'):
            current_mortgage = Mortgage.get_mortgage(self.initial_data['mortgage_id'])
            extra_payment = Payment(
                mortgage=current_mortgage,
                amount=self.initial_data['amount'],
                date=parse_date(self.initial_data['date']),
                is_extra=True
            )
            if not current_mortgage.first_payment_date < extra_payment.date < current_mortgage.last_payment_date:
                raise serializers.ValidationError({'date': responses.PAYMENT_DATE_INCORRECT})
            prev_payment = extra_payment.get_prev_payment()
            if extra_payment.amount > prev_payment.debt_rest:
                raise serializers.ValidationError({'amount': responses.PAYMENT_AMOUNT_INCORRECT})
        return attrs


class PaymentSerializer(BasicPaymentSerializer):
    class Meta(BasicPaymentSerializer.Meta):
        fields = BasicPaymentSerializer.Meta.fields + (
            'bank_amount', 'debt_decrease', 'debt_rest', 'is_extra')  # type: ignore
