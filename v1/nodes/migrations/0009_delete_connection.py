# Generated by Django 4.0.4 on 2022-06-11 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0008_alter_node_type'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Connection',
        ),
    ]
