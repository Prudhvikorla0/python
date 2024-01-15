# Generated by Django 4.0.4 on 2022-07-04 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0019_alter_currency_options_tenant_currencies'),
        ('supply_chains', '0027_rename_supplychain_connection_supply_chain_and_more'),
        ('bulk_templates', '0016_bulkupload_is_valid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkupload',
            name='supply_chain',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_uploads', to='supply_chains.supplychain', verbose_name='Supply Chain'),
        ),
        migrations.AddField(
            model_name='bulkupload',
            name='tenant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_uploads', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]
