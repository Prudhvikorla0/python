# Generated by Django 4.0.4 on 2022-06-27 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0019_node_trace_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodemember',
            name='type',
            field=models.IntegerField(choices=[(101, 'Super Admin'), (111, 'Admin'), (121, 'Connection Manager'), (131, 'Transaction Manager'), (141, 'Reporter')], default=111, verbose_name='Member Type'),
        ),
    ]
