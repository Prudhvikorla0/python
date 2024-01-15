# Generated by Django 4.0.4 on 2023-01-05 11:42
import json
from django.db import migrations

def update_regions(apps, schema_editor):
    """Create regions from country data json"""
    file = open('common/country_data/country_data_with_province_latlong.json')
    data = json.load(file)
    Country = apps.get_model('tenants', 'Country')
    Province = apps.get_model('tenants', 'Province')
    Region = apps.get_model('tenants', 'Region')
    a = ["Benin", "Burkina Faso", "Ghana", "Mali", "Nigeria", "Togo", "Côte d'Ivoire"]
    for country in a:
        country_object = Country.objects.get(name=country)
        for province in data[country]['sub_divisions'].keys():
            province_object, created = Province.objects.get_or_create(
                name=province, country=country_object)
            if 'region' in data[country]['sub_divisions'][province].keys():
                for region in data[country]['sub_divisions'][province]['region']:
                    reg, created = Region.objects.get_or_create(
                        name=region, province=province_object)


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0039_region_village'),
    ]

    operations = [
        migrations.RunPython(update_regions)
    ]
