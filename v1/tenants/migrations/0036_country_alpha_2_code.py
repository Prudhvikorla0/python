# Generated by Django 4.0.4 on 2023-01-03 10:06
import json
from django.db import migrations
from common.country_data import COUNTRIES


def populate_country_and_province_data(apps, schema_editor):
    Country = apps.get_model('tenants', 'Country')
    Province = apps.get_model('tenants', 'Province')
    Currency = apps.get_model('tenants', 'Currency')
    for country_name, extra_data in list(COUNTRIES.items()):
        country, _ = Country.objects.get_or_create(
            name=country_name)
        currency = Currency.objects.filter(code=extra_data['currency']).first()
        country.latitude = extra_data['latlong'][0]
        country.longitude = extra_data['latlong'][1]
        country.alpha_2 = extra_data['alpha_2']
        country.alpha_3 = extra_data['alpha_3']
        country.dial_code = extra_data['dial_code']
        country.currency = currency
        country.save()
        for province_name, loc_data in list(
            extra_data['sub_divisions'].items()):
            province, _ = Province.objects.get_or_create(
            name=province_name, country=country)
            province.latitude = loc_data['latlong'][0]
            province.longitude = loc_data['latlong'][1]
            province.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0035_country_alpha_3_alter_country_alpha_2'),
    ]

    operations = [
        migrations.RunPython(populate_country_and_province_data),
    ]
