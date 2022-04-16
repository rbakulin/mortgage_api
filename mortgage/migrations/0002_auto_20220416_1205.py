# Generated by Django 3.2.4 on 2022-04-16 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RealEstateObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Цена')),
                ('area', models.DecimalField(decimal_places=1, max_digits=5, verbose_name='Площадь')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
                ('built_year', models.IntegerField(verbose_name='Год постройки')),
            ],
            options={
                'db_table': 'real_estate_object',
            },
        ),
        migrations.AlterField(
            model_name='mortgage',
            name='first_payment_amount',
            field=models.DecimalField(decimal_places=2, max_digits=11, verbose_name='ПВ'),
        ),
        migrations.AlterField(
            model_name='mortgage',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Сумма кредита'),
        ),
    ]
