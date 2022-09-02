from django.db import models
from dateutil import relativedelta


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

    @property
    def period_in_months(self):
        return self.period * 12

    @property
    def last_payment_date(self):
        return self.issue_date + relativedelta.relativedelta(months=self.period * 12)

    class Meta:
        db_table = 'mortgage'
        ordering = ['id']


class Payment(CreatedUpdatedModel):
    date = models.DateField(null=True, blank=True, verbose_name="date")
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="amount")  # TODO: rename to sum?
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, null=True, related_name="payments",
                                 verbose_name='mortgage')
    is_extra = models.BooleanField(verbose_name='is extra payment', default=False)
    # TODO: rename to bank_amount?
    bank_share = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="bank share", null=True)
    debt_decrease = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt decrease", null=True)
    debt_rest = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt rest", null=True)

    def get_prev_payment(self):
        past_payments = Payment.objects.filter(mortgage_id=self.mortgage_id, date__lte=self.date).exclude(pk=self.pk)
        if past_payments:
            return sorted(list(past_payments), key=lambda payment: payment.date, reverse=True)[0]
        else:
            return None

    def get_next_payment(self):
        next_payments = Payment.objects.filter(mortgage_id=self.mortgage_id, date__gte=self.date).exclude(pk=self.pk)
        if next_payments:
            return sorted(list(next_payments), key=lambda payment: payment.date)[0]
        else:
            return None

    def calc_bank_share(self):
        prev_payment = self.get_prev_payment()
        if prev_payment:
            time_from_prev_payment = self.date - prev_payment.date
            debt_rest = prev_payment.debt_rest
        else:
            time_from_prev_payment = self.date - self.mortgage.issue_date
            debt_rest = self.mortgage.total_amount
        bank_percent = (debt_rest * self.mortgage.percent * time_from_prev_payment.days) / (365 * 100)
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
