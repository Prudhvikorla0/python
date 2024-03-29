# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_alter_tenantadmin_tenant'),
        ('products', '0002_batch_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quantity_units', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]
