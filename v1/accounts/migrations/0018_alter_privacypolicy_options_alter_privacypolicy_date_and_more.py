# Generated by Django 4.0.4 on 2022-08-02 10:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_privacypolicy_version'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='privacypolicy',
            options={'verbose_name_plural': 'Privacy Policies'},
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Privacy Policy Date'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='since',
            field=models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='version',
            field=models.PositiveIntegerField(default=0, unique=True, verbose_name='Version'),
        ),
    ]
