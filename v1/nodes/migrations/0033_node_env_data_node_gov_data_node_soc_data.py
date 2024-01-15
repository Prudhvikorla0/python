# Generated by Django 4.0.4 on 2023-04-24 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0022_alter_formfield_position'),
        ('nodes', '0032_alter_node_is_discoverable'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='env_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='env_data_node', to='dynamic_forms.formsubmission', verbose_name='Environment Data'),
        ),
        migrations.AddField(
            model_name='node',
            name='gov_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gov_data_node', to='dynamic_forms.formsubmission', verbose_name='Governance Data'),
        ),
        migrations.AddField(
            model_name='node',
            name='soc_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='soc_data_node', to='dynamic_forms.formsubmission', verbose_name='Social Data'),
        ),
    ]
