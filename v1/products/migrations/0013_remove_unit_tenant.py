# Generated by Django 4.0.4 on 2022-07-13 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_batch_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='tenant',
        ),
    ]
