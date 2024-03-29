# Generated by Django 4.0.4 on 2022-06-08 05:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_batch_product_alter_batch_tenant_and_more'),
        ('tenants', '0015_alter_province_country_alter_tenantadmin_tenant_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nodes', '0004_alter_node_country_alter_node_province'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='source_connections', to='nodes.node', verbose_name='Connected From'),
        ),
        migrations.AlterField(
            model_name='connection',
            name='supplychain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='products.supplychain', verbose_name='Supplychain'),
        ),
        migrations.AlterField(
            model_name='connection',
            name='target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target_connections', to='nodes.node', verbose_name='Connected To'),
        ),
        migrations.AlterField(
            model_name='connection',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='tenants.tenant', verbose_name='Tenant'),
        ),
        migrations.AlterField(
            model_name='node',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='tenants.tenant', verbose_name='Tenant'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='nodes.node', verbose_name='Node'),
        ),
        migrations.AlterField(
            model_name='nodemember',
            name='node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_members', to='nodes.node', verbose_name='Node'),
        ),
        migrations.AlterField(
            model_name='nodemember',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_members', to='tenants.tenant', verbose_name='Tenant'),
        ),
        migrations.AlterField(
            model_name='nodemember',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_nodes', to=settings.AUTH_USER_MODEL, verbose_name='Member User'),
        ),
    ]
