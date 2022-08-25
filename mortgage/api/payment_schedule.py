from math import pow
from decimal import Decimal
from datetime import datetime
from dateutil import relativedelta

from mortgage.models import Payment


class PaymentScheduler:
    def __init__(self, mortgage, extra_payment=None):
        self.mortgage = mortgage
        self.extra_payment = extra_payment
        self.extra_payment_date = datetime.strptime(extra_payment['date'], '%Y-%m-%d').date() if extra_payment else None

    def calc_payments_schedule(self, start_payment_number=1, amount=None):
        # TODO: make period in months in model
        period_in_months = self.mortgage.period * 12
        monthly_percent = Decimal(self.mortgage.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
        power = Decimal(pow(monthly_percent + 1, period_in_months))  # 1 - hardcode in math formula
        coef = Decimal(power * monthly_percent / (power - 1))

        amount = round(coef * self.mortgage.total_amount, 2) if not amount else amount

        for i in range(start_payment_number, period_in_months + 1):
            payment = Payment(
                mortgage=self.mortgage,
                amount=amount,
                date=self.mortgage.issue_date + relativedelta.relativedelta(months=i),
            )
            payment.bank_share = payment.calc_bank_share()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
            payment.save()

    def save_extra_payment(self):
        saving_method = PaymentScheduler.get_saving_method(self)
        return saving_method()

    def get_saving_method(self):
        for payment in Payment.objects.filter(mortgage_id=self.mortgage.pk):
            if payment.date == self.extra_payment_date:
                return self.same_date_saving

    def same_date_saving(self):
        # TODO: make it a credit's property
        last_payment_date = self.mortgage.issue_date + relativedelta.relativedelta(months=self.mortgage.period * 12)
        next_payment_date = self.extra_payment_date + relativedelta.relativedelta(months=1)
        time_left = relativedelta.relativedelta(last_payment_date, next_payment_date)
        # count of payments between extra payment and last payment
        months_left = time_left.months + time_left.years * 12
        monthly_percent = Decimal(self.mortgage.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
        power = Decimal(pow(monthly_percent + 1, months_left))  # 1 - hardcode in math formula
        coef = Decimal(power * monthly_percent / (power - 1))

        # extra payment
        payment = Payment(
            mortgage=self.mortgage,
            amount=self.extra_payment['amount'],
            date=self.extra_payment_date,
            is_extra=True
        )
        payment.bank_share = 0  # whole extra payment goes for debt decrease
        payment.debt_decrease = payment.calc_debt_decrease()
        payment.debt_rest = payment.calc_debt_rest()
        payment.save()

        next_payment = Payment.objects.get(mortgage_id=self.mortgage.pk, date=next_payment_date)
        time_between_payments = next_payment.date - payment.date
        days_between_payments = time_between_payments.days
        next_payment.amount = payment.debt_rest * self.mortgage.percent / 100 / 365 * days_between_payments
        next_payment.bank_share = next_payment.amount
        next_payment.debt_decrease = 0
        next_payment.debt_rest = payment.calc_debt_rest()
        next_payment.save()

        Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment_date).delete()

        start_payment_number = relativedelta.relativedelta(next_payment_date, self.mortgage.issue_date).months + 1
        amount = round(coef * payment.debt_rest, 2)
        self.calc_payments_schedule(start_payment_number, amount)
