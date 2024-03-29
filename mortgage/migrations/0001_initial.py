# Generated by Django 3.2.15 on 2022-09-06 09:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mortgage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('percent', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='percent')),
                ('period', models.IntegerField(verbose_name='period')),
                ('first_payment_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='first payment amount')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='total amount')),
                ('issue_date', models.DateField(verbose_name='issue date')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortgages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mortgage',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(verbose_name='date')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='amount')),
                ('is_extra', models.BooleanField(default=False, verbose_name='is extra payment')),
                ('bank_amount', models.DecimalField(decimal_places=2, max_digits=11, null=True, verbose_name='bank amount')),
                ('debt_decrease', models.DecimalField(decimal_places=2, max_digits=11, null=True, verbose_name='debt decrease')),
                ('debt_rest', models.DecimalField(decimal_places=2, max_digits=11, null=True, verbose_name='debt rest')),
                ('mortgage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='mortgage.mortgage', verbose_name='mortgage')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
    ]
