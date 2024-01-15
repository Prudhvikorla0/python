# Generated by Django 4.0.4 on 2023-02-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0041_alter_country_name_alter_currency_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='node_discoverability',
            field=models.IntegerField(choices=[(101, 'Always'), (201, 'Node Preference'), (301, 'Hidden (Still will be able to connect with Connect-ID)')], default=301, verbose_name='Node Discoverability'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='ci_availability',
            field=models.IntegerField(choices=[(101, 'CI Not Available'), (111, 'Tenant Level'), (121, 'Node Level')], default=111, verbose_name='Node Anonymity'),
        ),
    ]
