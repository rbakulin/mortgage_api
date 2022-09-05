from decimal import Decimal
from math import pow

from mortgage.models import Payment
from mortgage.helpers import get_timedelta, get_time_difference


class PaymentScheduler:
    def __init__(self, mortgage, extra_payment=None):
        self.mortgage = mortgage
        self.extra_payment = extra_payment

    def calc_and_save_payments_schedule(self, start_payment_number=1, amount=None):
        # 1 - hardcode in math formula
        power = Decimal(pow(self.mortgage.monthly_percent + 1, self.mortgage.period_in_months))
        coef = Decimal(power * self.mortgage.monthly_percent / (power - 1))
        amount = round(coef * self.mortgage.total_amount, 2) if not amount else amount
        before_last_rest = None

        for i in range(start_payment_number, self.mortgage.period_in_months):
            payment = Payment(
                mortgage=self.mortgage,
                amount=amount,
                date=self.mortgage.issue_date + get_timedelta(months=i),
            )
            payment.bank_amount = payment.calc_bank_amount()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
            payment.save()
            before_last_rest = payment.debt_rest

        # add last payment manually
        payment = Payment(
            mortgage=self.mortgage,
            amount=before_last_rest,  # the amount of last payment is equal to previous payment's debt rest
            date=self.mortgage.last_payment_date,
        )
        payment.bank_amount = payment.calc_bank_amount()
        payment.debt_decrease = payment.calc_debt_decrease()
        payment.debt_rest = 0
        payment.save()

    def save_extra_payment(self):
        saving_method = PaymentScheduler.get_saving_method(self)
        return saving_method()

    def get_saving_method(self):
        for payment in Payment.objects.filter(mortgage_id=self.mortgage.pk):
            if payment.date == self.extra_payment.date:
                return self.same_date_saving

        extra_payment = self.extra_payment
        extra_payment.bank_amount = extra_payment.calc_bank_amount()
        if extra_payment.amount <= extra_payment.bank_amount:
            return self.less_than_bank_percent_saving
        else:
            return self.more_than_bank_percent_saving

    def same_date_saving(self):
        extra_payment = self.extra_payment
        extra_payment.bank_amount = 0  # whole extra payment goes for debt decrease
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()

        next_payment = self.extra_payment.get_next_payment()
        if next_payment:
            next_payment.amount = next_payment.calc_bank_amount()
            next_payment.bank_amount = next_payment.amount
            next_payment.debt_decrease = 0
            next_payment.debt_rest = next_payment.calc_debt_rest() - next_payment.debt_decrease
            next_payment.save()

            Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment.date).delete()

            start_payment_number, amount = self.get_new_schedule_parameters(next_payment)
            self.calc_and_save_payments_schedule(start_payment_number, amount)

    def less_than_bank_percent_saving(self):
        extra_payment = self.extra_payment
        extra_payment.bank_amount = self.extra_payment['amount']
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()

        next_payment = extra_payment.get_next_payment()
        if next_payment:
            next_payment.amount = next_payment.amount - self.extra_payment['amount']
            next_payment.bank_amount = next_payment.calc_bank_amount()
            next_payment.debt_decrease = next_payment.calc_debt_decrease()
            next_payment.debt_rest = next_payment.calc_debt_rest()
            next_payment.save()

    def more_than_bank_percent_saving(self):
        extra_payment = self.extra_payment
        extra_payment.bank_amount = extra_payment.calc_bank_amount()
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()

        next_payment = extra_payment.get_next_payment()
        if next_payment:
            next_payment.bank_amount = next_payment.calc_bank_amount()
            next_payment.amount = next_payment.bank_amount
            next_payment.debt_decrease = next_payment.calc_debt_decrease()
            next_payment.debt_rest = next_payment.calc_debt_rest()
            next_payment.save()

            Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment.date).delete()

            start_payment_number, amount = self.get_new_schedule_parameters(next_payment)
            self.calc_and_save_payments_schedule(start_payment_number, amount)

    def get_new_schedule_parameters(self, next_payment):
        time_left = get_time_difference(self.mortgage.last_payment_date, next_payment.date)
        months_left = time_left.months + time_left.years * 12  # count of payments between extra and last payments
        power = Decimal(pow(self.mortgage.monthly_percent + 1, months_left))
        coef = Decimal(power * self.mortgage.monthly_percent / (power - 1))

        start_payment_number = get_time_difference(next_payment.date, self.mortgage.issue_date).months + 1
        amount = round(coef * self.extra_payment.debt_rest, 2)
        return start_payment_number, amount