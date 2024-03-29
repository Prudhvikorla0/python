# Generated by Django 4.0.4 on 2022-08-09 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0031_alter_supplychain_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='name_en_uk',
            field=models.CharField(default='', max_length=100, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='operation',
            name='name_en_us',
            field=models.CharField(default='', max_length=100, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='operation',
            name='name_fr',
            field=models.CharField(default='', max_length=100, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='operation',
            name='name_nl',
            field=models.CharField(default='', max_length=100, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='description_en_uk',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='description_en_us',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='description_fr',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='description_nl',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='name_en_uk',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Supply Chain Name'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='name_en_us',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Supply Chain Name'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='name_fr',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Supply Chain Name'),
        ),
        migrations.AddField(
            model_name='supplychain',
            name='name_nl',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Supply Chain Name'),
        ),
    ]
