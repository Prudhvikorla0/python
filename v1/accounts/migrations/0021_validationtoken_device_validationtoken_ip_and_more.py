# Generated by Django 4.0.4 on 2022-09-04 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_privacypolicy_content_en_uk_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationtoken',
            name='device',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='validationtoken',
            name='ip',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='validationtoken',
            name='location',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
