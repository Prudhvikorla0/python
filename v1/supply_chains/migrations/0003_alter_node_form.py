# Generated by Django 4.0.4 on 2022-05-17 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0002_initial'),
        ('supply_chains', '0002_alter_node_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nod', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
    ]
