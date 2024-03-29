# Generated by Django 4.0.4 on 2022-05-18 11:53

import common.library
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0006_node_city_node_contact_name_node_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='operations',
            field=models.ManyToManyField(blank=True, default=None, related_name='nodes', to='supply_chains.operation', verbose_name='Categories'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='description',
            field=models.CharField(default='', max_length=2000, verbose_name='File Description'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='file',
            field=models.FileField(blank=True, default=None, max_length=500, null=True, upload_to=common.library._get_file_path, verbose_name='Document'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='name',
            field=models.CharField(default='', max_length=500, verbose_name='File Name'),
        ),
        migrations.AlterField(
            model_name='nodedocument',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supply_chains.node', verbose_name='Node'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='image',
            field=models.FileField(blank=True, upload_to=common.library._get_file_path, verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='name',
            field=models.CharField(default='', max_length=100, null=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='node_type',
            field=models.IntegerField(choices=[(101, 'Company'), (111, 'Farmer')], default=101, verbose_name='Type Of Node'),
        ),
    ]
