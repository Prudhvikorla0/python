# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0003_alter_formfield_options_alter_formfieldvalue_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfieldvalue',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='dynamic_forms.formsubmission', verbose_name='Form'),
        ),
    ]
