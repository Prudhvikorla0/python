# Generated by Django 4.0.4 on 2023-07-05 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0036_alter_node_tenant_alter_nodedocument_file_and_more'),
        ('tenants', '0046_alter_category_tenant_alter_tenantadmin_tenant_and_more'),
        ('supply_chains', '0042_connection_submission_form_mongo_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodesupplychain',
            name='node',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='supply_chains', to='nodes.node', verbose_name='Node'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='tenant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='connection_tags', to='tenants.tenant', verbose_name='Tenant'),
            preserve_default=False,
        ),
    ]
