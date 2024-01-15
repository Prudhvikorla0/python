# Generated by Django 4.0.4 on 2023-04-25 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0023_form_description_form_name'),
        ('nodes', '0033_node_env_data_node_gov_data_node_soc_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='env_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='env_data_node', to='dynamic_forms.formsubmission', verbose_name='Environment Data'),
        ),
        migrations.AlterField(
            model_name='node',
            name='gov_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gov_data_node', to='dynamic_forms.formsubmission', verbose_name='Governance Data'),
        ),
        migrations.AlterField(
            model_name='node',
            name='inviter_questionnaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invited_node_questionnaire', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='node',
            name='signup_questionnaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='self_signup_questionnaire', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='node',
            name='soc_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='soc_data_node', to='dynamic_forms.formsubmission', verbose_name='Social Data'),
        ),
        migrations.AlterField(
            model_name='node',
            name='submission_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_node', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='nodemember',
            name='submission_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='node_member', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
    ]
