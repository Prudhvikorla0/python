# Generated by Django 4.0.4 on 2023-11-10 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0038_node_company_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodedocument',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='File Description'),
        ),
    ]
