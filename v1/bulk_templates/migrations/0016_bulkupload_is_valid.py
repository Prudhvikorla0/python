# Generated by Django 4.0.4 on 2022-07-03 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0015_remove_bulkupload_actors_added_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkupload',
            name='is_valid',
            field=models.BooleanField(default=False, verbose_name='Is file data valid'),
        ),
    ]
