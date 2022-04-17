# Generated by Django 3.2.4 on 2022-04-16 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0002_auto_20220416_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Сумма')),
                ('bank_percent', models.DecimalField(decimal_places=1, max_digits=5, verbose_name='Процент банку')),
                ('debt_decrease', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Уменьшение долга')),
                ('debt_rest', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Остаток долга')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
    ]