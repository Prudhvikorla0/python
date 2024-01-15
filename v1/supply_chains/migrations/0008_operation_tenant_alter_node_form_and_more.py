# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_alter_tenantadmin_tenant'),
        ('dynamic_forms', '0004_alter_formfieldvalue_form'),
        ('supply_chains', '0007_alter_node_operations_alter_nodedocument_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_operations', to='tenants.tenant', verbose_name='Tenant'),
        ),
        migrations.AlterField(
            model_name='node',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_node', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='supply_chains.node', verbose_name='Node'),
        ),
        migrations.AlterField(
            model_name='nodemember',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membebers', to='supply_chains.node', verbose_name='Node'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_tags', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]