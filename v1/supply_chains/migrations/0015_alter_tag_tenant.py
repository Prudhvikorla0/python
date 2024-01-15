# Generated by Django 4.0.4 on 2022-06-08 05:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0015_alter_province_country_alter_tenantadmin_tenant_and_more'),
        ('supply_chains', '0014_remove_connection_creator_remove_connection_form_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connection_tags', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]