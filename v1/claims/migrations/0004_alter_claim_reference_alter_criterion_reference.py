# Generated by Django 4.0.4 on 2022-05-17 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0003_alter_claim_reference_alter_criterion_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='b2WqvWrmoVIyS8lz', max_length=16, verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='criterion',
            name='reference',
            field=models.CharField(default='7OVJz0bF0SkvCj6h', max_length=16, verbose_name='Reference Number'),
        ),
    ]
