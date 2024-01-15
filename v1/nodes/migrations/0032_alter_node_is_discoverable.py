# Generated by Django 4.0.4 on 2023-02-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0031_node_connect_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='is_discoverable',
            field=models.BooleanField(default=False, verbose_name='Is Node Discoverable To Others. Will always be discoverable with Connect-ID'),
        ),
    ]