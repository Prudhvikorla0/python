# Generated by Django 4.0.4 on 2022-05-18 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0006_alter_country_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='provinces',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
