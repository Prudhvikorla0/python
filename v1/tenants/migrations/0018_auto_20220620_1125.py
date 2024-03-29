# Generated by Django 4.0.4 on 2022-06-20 11:25

from django.db import migrations

from common.currencies import CURRENCY_CHOICES as currencies


def populate_currencies(apps, schema_editor):
    """
    Function populate currency model with currency data.
    """
    Currency = apps.get_model('tenants', 'Currency')
    for currency in currencies:
        Currency.objects.get_or_create(
            name=currency[1], code=currency[0])


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0017_currency'),
    ]

    operations = [
        migrations.RunPython(populate_currencies),
    ]
