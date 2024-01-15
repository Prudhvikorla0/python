# Generated by Django 4.0.4 on 2022-06-15 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0011_node_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='connections',
            field=models.ManyToManyField(related_name='incoming_connections', through='supply_chains.Connection', to='nodes.node', verbose_name='Node Connections'),
        ),
    ]