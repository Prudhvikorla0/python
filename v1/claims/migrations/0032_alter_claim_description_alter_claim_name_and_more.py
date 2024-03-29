# Generated by Django 4.0.4 on 2022-07-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0031_attachedclaim_message_hash_attachedclaim_message_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='description',
            field=models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='name',
            field=models.CharField(max_length=500, verbose_name='Claim'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='', max_length=16, null=True, verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='criterion',
            name='reference',
            field=models.CharField(default='', max_length=16, null=True, verbose_name='Reference Number'),
        ),
    ]
