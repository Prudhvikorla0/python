# Generated by Django 4.0.4 on 2022-07-24 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0025_bulkupload_new_items_failed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkupload',
            name='file_name',
            field=models.CharField(default='bulk_file.xlsx', max_length=100, verbose_name='File Name'),
            preserve_default=False,
        ),
    ]