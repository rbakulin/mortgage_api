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

    class Meta:
        db_table = 'mortgage'
        ordering = ['id']


class Payment(CreatedUpdatedModel):
    date = models.DateField(null=True, blank=True, verbose_name="date")
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="amount")
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, null=True, related_name="payments",
                                 verbose_name='mortgage')

    def get_prev_payment(self):
        past_payments = Payment.objects.filter(mortgage_id=self.mortgage_id, date__lt=self.date)
        if past_payments:
            return sorted(list(past_payments), key=lambda payment: payment.date, reverse=True)[0]
        else:
            return None

    @property
    def bank_share(self):
        prev_payment = self.get_prev_payment()
        if prev_payment:
            days_from_prev_payment = self.date - prev_payment.date
            debt_rest = prev_payment.debt_rest
        else:
            days_from_prev_payment = self.date - self.mortgage.issue_date
            debt_rest = self.mortgage.total_amount
        bank_percent = (debt_rest * self.mortgage.percent * days_from_prev_payment.days) / (365 * 100)
        return round(bank_percent, 2)

    @property
    def debt_decrease(self):
        return self.amount - self.bank_share

    @property
    def debt_rest(self):
        prev_payment = self.get_prev_payment()
        if prev_payment:
            prev_amount = prev_payment.debt_rest
        else:
            prev_amount = self.mortgage.total_amount
        return prev_amount - self.debt_decrease

    class Meta:
        db_table = 'payment'
