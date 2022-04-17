# Generated by Django 3.2.4 on 2022-04-16 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mortgage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('percent', models.DecimalField(decimal_places=2, max_digits=2, verbose_name='Процент')),
                ('period', models.IntegerField(verbose_name='Срок кредита')),
                ('first_payment_amount', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='ПВ')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Сумма кредита')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='Дата выдачи')),
            ],
            options={
                'db_table': 'mortgage',
            },
        ),
    ]