# Generated by Django 4.0.4 on 2022-07-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_customuser_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='validationtoken',
            name='key',
            field=models.CharField(max_length=200, verbose_name='Token'),
        ),
    ]