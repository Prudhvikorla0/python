# Generated by Django 4.0.4 on 2022-12-04 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0033_alter_template_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatefieldtype',
            name='is_dynamic',
            field=models.BooleanField(default=False),
        ),
    ]
