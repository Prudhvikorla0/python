# Generated by Django 4.0.4 on 2022-08-09 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0018_formfieldvalue_file_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldvalueoption',
            name='name_en_uk',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Option'),
        ),
        migrations.AddField(
            model_name='fieldvalueoption',
            name='name_en_us',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Option'),
        ),
        migrations.AddField(
            model_name='fieldvalueoption',
            name='name_fr',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Option'),
        ),
        migrations.AddField(
            model_name='fieldvalueoption',
            name='name_nl',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Option'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='info_en_uk',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='More Info'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='info_en_us',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='More Info'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='info_fr',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='More Info'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='info_nl',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='More Info'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_en_uk',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_en_us',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_fr',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_nl',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='place_holder_en_uk',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Place Holder'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='place_holder_en_us',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Place Holder'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='place_holder_fr',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Place Holder'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='place_holder_nl',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Place Holder'),
        ),
    ]
