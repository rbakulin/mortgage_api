from math import pow
from decimal import Decimal
from dateutil import relativedelta

from mortgage.models import Payment


class PaymentScheduler:
    def __init__(self, mortgage, extra_payment=None):
        self.mortgage = mortgage
        self.extra_payment = extra_payment

    def calc_payments_schedule(self, start_payment_number=1, amount=None):
        monthly_percent = Decimal(self.mortgage.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
        power = Decimal(pow(monthly_percent + 1, self.mortgage.period_in_months))  # 1 - hardcode in math formula
        coef = Decimal(power * monthly_percent / (power - 1))

        amount = round(coef * self.mortgage.total_amount, 2) if not amount else amount

        for i in range(start_payment_number, self.mortgage.period_in_months + 1):
            payment = Payment(
                mortgage=self.mortgage,
                amount=amount,
                date=self.mortgage.issue_date + relativedelta.relativedelta(months=i),
            )
            payment.bank_amount = payment.calc_bank_amount()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
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
        # TODO: use get_next_payment()
        next_payment_date = self.extra_payment.date + relativedelta.relativedelta(months=1)
        time_left = relativedelta.relativedelta(self.mortgage.last_payment_date, next_payment_date)
        # count of payments between extra payment and last payment
        months_left = time_left.months + time_left.years * 12
        monthly_percent = Decimal(self.mortgage.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
        power = Decimal(pow(monthly_percent + 1, months_left))  # 1 - hardcode in math formula
        coef = Decimal(power * monthly_percent / (power - 1))

        extra_payment = self.extra_payment
        extra_payment.bank_amount = 0  # whole extra payment goes for debt decrease
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()

        next_payment = Payment.objects.get(mortgage_id=self.mortgage.pk, date=next_payment_date)
        time_between_payments = next_payment.date - extra_payment.date
        days_between_payments = time_between_payments.days
        next_payment.amount = extra_payment.debt_rest * self.mortgage.percent / 100 / 365 * days_between_payments
        next_payment.bank_amount = next_payment.amount
        next_payment.debt_decrease = 0
        next_payment.debt_rest = next_payment.calc_debt_rest()
        next_payment.save()

        Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment_date).delete()

        start_payment_number = relativedelta.relativedelta(next_payment_date, self.mortgage.issue_date).months + 1
        amount = round(coef * extra_payment.debt_rest, 2)
        self.calc_payments_schedule(start_payment_number, amount)

    def less_than_bank_percent_saving(self):
        extra_payment = self.extra_payment
        extra_payment.bank_amount = self.extra_payment['amount']
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()

        # TODO: if there is no next payment?
        next_payment = extra_payment.get_next_payment()
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

        # TODO: if there is no next payment?
        next_payment = extra_payment.get_next_payment()
        next_payment.bank_amount = next_payment.calc_bank_amount()
        next_payment.amount = next_payment.bank_amount
        next_payment.debt_decrease = next_payment.calc_debt_decrease()
        next_payment.debt_rest = next_payment.calc_debt_rest()
        next_payment.save()

        Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment.date).delete()

        # TODO: use get_next_payment()
        time_left = relativedelta.relativedelta(self.mortgage.last_payment_date, next_payment.date)
        # count of payments between extra payment and last payment
        months_left = time_left.months + time_left.years * 12
        monthly_percent = Decimal(self.mortgage.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
        power = Decimal(pow(monthly_percent + 1, months_left))  # 1 - hardcode in math formula
        coef = Decimal(power * monthly_percent / (power - 1))

        start_payment_number = relativedelta.relativedelta(next_payment.date, self.mortgage.issue_date).months + 1
        amount = round(coef * next_payment.debt_rest, 2)
        self.calc_payments_schedule(start_payment_number, amount)
