# Generated by Django 4.0.4 on 2022-06-22 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0010_templatefield_width_templatefieldtype_width_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatefield',
            name='column_pos',
            field=models.CharField(blank=True, default='A', max_length=4, null=True, verbose_name='Column Position'),
        ),
    ]