# Generated by Django 4.0.4 on 2022-06-08 05:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_customuser_default_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesstoken',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authe_token', to=settings.AUTH_USER_MODEL, verbose_name='Token User'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL, verbose_name='Device User'),
        ),
        migrations.AlterField(
            model_name='validationtoken',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='validation_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Token User'),
        ),
    ]