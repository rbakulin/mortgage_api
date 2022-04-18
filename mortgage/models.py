from django.db import models


class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Mortgage(CreatedUpdatedModel):
    percent = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Процент")
    period = models.IntegerField(verbose_name="Срок кредита")
    first_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="ПВ")
    total_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Сумма кредита")
    issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи")
    real_estate_object = models.ForeignKey('RealEstateObject', unique=True, on_delete=models.CASCADE, null=True,
                                           verbose_name='Объект недвижимости')

    class Meta:
        db_table = 'mortgage'


class RealEstateObject(CreatedUpdatedModel):
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Цена")
    area = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Площадь")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    built_year = models.IntegerField(verbose_name='Год постройки')

    class Meta:
        db_table = 'real_estate_object'


class Payment(CreatedUpdatedModel):
    date = models.DateField(null=True, blank=True, verbose_name="Дата")
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Сумма")
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, null=True, verbose_name='Ипотечный кредит')

    def get_prev_payment(self):
        past_payments = Payment.objects.filter(mortgage_id=self.mortgage_id, date__lt=self.date)
        if past_payments:
            return sorted(list(past_payments), key=lambda payment: payment.date, reverse=True)[0]
        else:
            return None

    @property
    def bank_percent(self):
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
        return self.amount - self.bank_percent

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
