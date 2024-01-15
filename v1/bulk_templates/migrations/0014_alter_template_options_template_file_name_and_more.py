# Generated by Django 4.0.4 on 2022-06-30 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0019_alter_currency_options_tenant_currencies'),
        ('bulk_templates', '0013_template_description_alter_template_data_row_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='template',
            options={},
        ),
        migrations.AddField(
            model_name='template',
            name='file_name',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Template File Name'),
        ),
        migrations.AlterUniqueTogether(
            name='template',
            unique_together={('tenant', 'type')},
        ),
    ]