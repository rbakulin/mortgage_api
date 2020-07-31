from django.db import models


class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Credit(CreatedUpdatedModel):
    object_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Стоимость недвижимости")
    first_payment_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="ПВ")
    percent = models.DecimalField(max_digits=2, decimal_places=2, verbose_name="Процент")
    payment_period = models.IntegerField(verbose_name="Срок погашения в годах")
    payment_start = models.DateField()

    class Meta:
        db_table = 'credit'
