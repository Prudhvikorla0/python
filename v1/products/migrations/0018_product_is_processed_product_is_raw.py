# Generated by Django 4.0.4 on 2023-05-15 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_batch_name_en_uk_batch_name_en_us_batch_name_fr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_processed',
            field=models.BooleanField(default=False, verbose_name='Is Processed Product'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_raw',
            field=models.BooleanField(default=False, verbose_name='Is Raw Product'),
        ),
    ]