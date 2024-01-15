# Generated by Django 4.0.4 on 2023-04-24 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0022_alter_formfield_position'),
        ('tenants', '0042_tenant_node_discoverability_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='env_data_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='env_form_tenant', to='dynamic_forms.form', verbose_name='Environment Data Form'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='gov_data_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gov_form_tenant', to='dynamic_forms.form', verbose_name='Governance Data Form'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='soc_data_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='soc_form_tenant', to='dynamic_forms.form', verbose_name='Social Data Form'),
        ),
    ]
