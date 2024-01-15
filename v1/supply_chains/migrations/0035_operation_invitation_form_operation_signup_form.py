# Generated by Django 4.0.4 on 2023-01-02 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0021_formfieldvalue_company_document'),
        ('supply_chains', '0034_auto_20221109_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='invitation_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitation_form_operation', to='dynamic_forms.form', verbose_name='Extra Fields For Invitation'),
        ),
        migrations.AddField(
            model_name='operation',
            name='signup_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='signup_form_operation', to='dynamic_forms.form', verbose_name='Extra Fields For Signup'),
        ),
    ]
