# Generated by Django 4.0.4 on 2022-09-03 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0030_alter_templatefieldtype_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatefield',
            name='can_read',
            field=models.BooleanField(default=True, verbose_name='Can Read'),
        ),
        migrations.AddField(
            model_name='templatefield',
            name='can_write',
            field=models.BooleanField(default=True, verbose_name='Can Write'),
        ),
    ]