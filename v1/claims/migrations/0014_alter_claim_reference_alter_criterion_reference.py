# Generated by Django 4.0.4 on 2022-05-18 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0013_alter_claim_reference_alter_criterion_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='RPRsaqsm1pxnrMsr', max_length=16, verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='criterion',
            name='reference',
            field=models.CharField(default='DOpHfxMyuPJYyD8q', max_length=16, verbose_name='Reference Number'),
        ),
    ]
