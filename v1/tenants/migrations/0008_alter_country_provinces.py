# Generated by Django 4.0.4 on 2022-05-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0007_alter_country_provinces'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='provinces',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Provinces'),
        ),
    ]
