# Generated by Django 4.0.4 on 2022-06-08 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0007_alter_connection_supplychain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='type',
            field=models.IntegerField(choices=[(101, 'Company'), (111, 'Producer')], default=101, verbose_name='Node Type'),
        ),
    ]
