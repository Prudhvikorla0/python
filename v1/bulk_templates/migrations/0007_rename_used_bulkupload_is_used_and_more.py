# Generated by Django 4.0.4 on 2022-06-19 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0006_rename_farmers_added_bulkupload_actors_added_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bulkupload',
            old_name='used',
            new_name='is_used',
        ),
        migrations.RenameField(
            model_name='template',
            old_name='default',
            new_name='is_default',
        ),
    ]
