# Generated by Django 4.0.4 on 2022-05-17 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0011_alter_claim_reference_alter_criterion_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='PravVVKeq6TKLkXB', max_length=16, verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='criterion',
            name='reference',
            field=models.CharField(default='D8JBPKc7nPe6rwNy', max_length=16, verbose_name='Reference Number'),
        ),
    ]
