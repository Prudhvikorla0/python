# Generated by Django 4.0.4 on 2022-07-04 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0021_alter_nodemember_options_node_is_discoverable_and_more'),
        ('tenants', '0020_alter_tenantadmin_options_tenant_blockchain_logging_and_more'),
        ('supply_chains', '0029_alter_nodesupplychain_supply_chain'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nodesupplychain',
            options={},
        ),
        migrations.AlterModelOptions(
            name='operation',
            options={},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='nodesupplychain',
            unique_together={('supply_chain', 'node')},
        ),
        migrations.AlterUniqueTogether(
            name='operation',
            unique_together={('tenant', 'node_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('tenant', 'name')},
        ),
    ]
