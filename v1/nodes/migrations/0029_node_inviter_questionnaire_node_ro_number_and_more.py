# Generated by Django 4.0.4 on 2023-01-02 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0021_formfieldvalue_company_document'),
        ('nodes', '0028_node_upload_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='inviter_questionnaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_node_questionnaire', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AddField(
            model_name='node',
            name='ro_number',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Right Origins Identity Number'),
        ),
        migrations.AddField(
            model_name='node',
            name='signup_questionnaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='self_signup_questionnaire', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
    ]
