# Generated by Django 4.0.4 on 2022-06-15 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0023_remove_connection_source_tags_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
