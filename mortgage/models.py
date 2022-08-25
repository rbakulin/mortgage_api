from math import pow
from decimal import Decimal
from datetime import datetime
from dateutil import relativedelta
from django.db import models


class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Mortgage(CreatedUpdatedModel):
    percent = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="percent")
    period = models.IntegerField(verbose_name="period")
    first_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="first payment amount")
    apartment_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="apartment price", null=True)
    total_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="total amount")
    issue_date = models.DateField(null=True, blank=True, verbose_name="issue date")
    user = models.ForeignKey('auth.User', related_name='mortgages', on_delete=models.CASCADE, null=True)

    # TODO: - make extra_payment a separate function
    #       - make count_payments and save_payments separate
    def calc_payments_schedule(self, extra_payment=None):
        # TODO: make period in months in model
        period_in_months = self.period * 12
        if extra_payment:
            extra_payment_date = datetime.strptime(extra_payment['date'], '%Y-%m-%d').date()
            is_same_date = False
            for payment in Payment.objects.filter(mortgage_id=self.pk):
                if payment.date == extra_payment_date:
                    is_same_date = True
            if is_same_date:
                # TODO: make it a credit's property
                last_payment_date = self.issue_date + relativedelta.relativedelta(months=self.period * 12)
                time_left = relativedelta.relativedelta(last_payment_date, extra_payment_date)
                # count of payments between extra payment and last payment
                months_left = time_left.months + time_left.years * 12
                monthly_percent = Decimal(self.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format
                power = Decimal(pow(monthly_percent + 1, months_left))  # 1 - hardcode in math formula
                coef = Decimal(power * monthly_percent / (power - 1))
                amount = round(coef * (self.total_amount - extra_payment['amount']), 2)

                payment = Payment()
                payment.mortgage = self
                payment.amount = extra_payment['amount']
                payment.date = extra_payment_date
                payment.is_extra = True
                payment.bank_share = 0  # whole extra payment goes for debt decrease
                payment.debt_decrease = payment.calc_debt_decrease()
                payment.debt_rest = payment.calc_debt_rest()
                payment.save()

                next_payment_date = extra_payment_date + relativedelta.relativedelta(months=1)
                next_payment = Payment.objects.get(mortgage_id=self.pk, date=next_payment_date)
                # next payment after extra is equal to amount of bank share
                next_payment.amount = next_payment.bank_share
                next_payment.debt_decrease = 0
                next_payment.debt_rest = payment.calc_debt_rest()
                next_payment.save()

                Payment.objects.filter(mortgage_id=self.pk, date__gt=next_payment_date).delete()

                start_payment_number = relativedelta.relativedelta(next_payment_date, self.issue_date).months + 1

            else:
                pass
        else:
            dem = Decimal(self.percent / 1200 + 1)
            power = Decimal(pow(dem, period_in_months))
            coef = Decimal(power * (dem - 1) / (power - 1))
            amount = round(coef * self.total_amount, 2)
            start_payment_number = 1

        for i in range(start_payment_number, period_in_months + 1):
            payment = Payment()
            payment.mortgage = self
            payment.amount = amount
            payment.date = self.issue_date + relativedelta.relativedelta(months=i)
            payment.bank_share = payment.calc_bank_share()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
            payment.save()

    class Meta:
        db_table = 'mortgage'
        ordering = ['id']


class Payment(CreatedUpdatedModel):
    date = models.DateField(null=True, blank=True, verbose_name="date")
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="amount")  # TODO: rename to sum?
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, null=True, related_name="payments",
                                 verbose_name='mortgage')
    is_extra = models.BooleanField(verbose_name='is extra payment', default=False)
    # TODO: rename to bank_sum?
    bank_share = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="bank share", null=True)
    debt_decrease = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt decrease", null=True)
    debt_rest = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt rest", null=True)

    def get_prev_payment(self):
        past_payments = Payment.objects.filter(mortgage_id=self.mortgage_id, date__lt=self.date)
        if past_payments:
            return sorted(list(past_payments), key=lambda payment: payment.date, reverse=True)[0]
        else:
            return None

    def calc_bank_share(self):
        prev_payment = self.get_prev_payment()
        if prev_payment:
            days_from_prev_payment = self.date - prev_payment.date
            debt_rest = prev_payment.debt_rest
        else:
            days_from_prev_payment = self.date - self.mortgage.issue_date
            debt_rest = self.mortgage.total_amount
        bank_percent = (debt_rest * self.mortgage.percent * days_from_prev_payment.days) / (365 * 100)
        return round(bank_percent, 2)

    def calc_debt_decrease(self):
        return self.amount - self.bank_share

    def calc_debt_rest(self):
        prev_payment = self.get_prev_payment()
        if prev_payment:
            prev_amount = prev_payment.debt_rest
        else:
            prev_amount = self.mortgage.total_amount
        return prev_amount - self.debt_decrease

    class Meta:
        db_table = 'payment'
