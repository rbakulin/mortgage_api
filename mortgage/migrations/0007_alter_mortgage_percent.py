# Generated by Django 3.2.20 on 2023-09-11 10:35

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0006_alter_mortgage_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mortgage',
            name='percent',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.1')), django.core.validators.MaxValueValidator(100)], verbose_name='bank percent'),
        ),
    ]