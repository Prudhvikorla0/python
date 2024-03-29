# Generated by Django 4.0.4 on 2023-04-24 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0022_alter_formfield_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Form Description'),
        ),
        migrations.AddField(
            model_name='form',
            name='name',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Form Name'),
        ),
    ]
