# Generated by Django 4.0.4 on 2022-06-08 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_batch_product_alter_batch_tenant_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplychain',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='supplychain',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='supplychain',
            name='updater',
        ),
    ]
