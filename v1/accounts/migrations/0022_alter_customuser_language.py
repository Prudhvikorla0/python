# Generated by Django 4.0.4 on 2022-09-07 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_validationtoken_device_validationtoken_ip_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('nl', 'Dutch'), ('de', 'German'), ('fr', 'French')], default='en', max_length=10, verbose_name='Selected Language'),
        ),
    ]
