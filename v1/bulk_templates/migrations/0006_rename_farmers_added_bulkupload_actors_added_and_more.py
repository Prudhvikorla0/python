# Generated by Django 4.0.4 on 2022-06-08 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0005_alter_bulkupload_node_alter_template_tenant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bulkupload',
            old_name='farmers_added',
            new_name='actors_added',
        ),
        migrations.RenameField(
            model_name='bulkupload',
            old_name='farmers_to_add',
            new_name='actors_to_add',
        ),
        migrations.RenameField(
            model_name='bulkupload',
            old_name='farmers_to_update',
            new_name='actors_to_update',
        ),
        migrations.RenameField(
            model_name='bulkupload',
            old_name='farmers_updated',
            new_name='actors_updated',
        ),
    ]
