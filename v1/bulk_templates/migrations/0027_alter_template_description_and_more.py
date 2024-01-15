# Generated by Django 4.0.4 on 2022-07-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0026_bulkupload_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Excel Description'),
        ),
        migrations.AlterField(
            model_name='templatefieldtype',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description About Field'),
        ),
    ]