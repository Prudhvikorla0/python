# Generated by Django 4.0.4 on 2022-08-09 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0025_tenant_batch_claim_tenant_bulk_upload_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tenant',
            old_name='company_claim',
            new_name='node_claim',
        ),
    ]
