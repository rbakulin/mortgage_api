# Generated by Django 3.2.4 on 2022-05-12 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0009_auto_20220418_1755'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mortgage',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='mortgage',
            name='real_estate_object',
        ),
        migrations.AddField(
            model_name='mortgage',
            name='apartment_price',
            field=models.DecimalField(decimal_places=2, max_digits=11, null=True, verbose_name='apartment price'),
        ),
        migrations.DeleteModel(
            name='RealEstateObject',
        ),
    ]