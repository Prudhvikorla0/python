# Generated by Django 4.0.4 on 2022-06-08 05:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0007_alter_formfield_options_alter_formfieldvalue_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='dynamic_forms.form', verbose_name='Form'),
        ),
        migrations.AlterField(
            model_name='formfieldvalue',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='values', to='dynamic_forms.formfield', verbose_name='Field'),
        ),
        migrations.AlterField(
            model_name='formfieldvalue',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='dynamic_forms.formsubmission', verbose_name='Form'),
        ),
        migrations.AlterField(
            model_name='formsubmission',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_forms', to='dynamic_forms.form', verbose_name='Form'),
        ),
    ]
