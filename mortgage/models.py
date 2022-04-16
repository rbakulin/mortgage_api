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
    bank_percent = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Процент банку")
    debt_decrease = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Уменьшение долга")
    debt_rest = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Остаток долга")
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, null=True, verbose_name='Ипотечный кредит')

    class Meta:
        db_table = 'payment'
