# Generated by Django 4.0.4 on 2023-01-03 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0031_remove_currency_country_country_currency'),
        ('tenants', '0031_tenant_non_producer_stock_creation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='country',
            old_name='code',
            new_name='alpha_2',
        ),
    ]