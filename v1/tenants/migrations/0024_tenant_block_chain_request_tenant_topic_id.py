# Generated by Django 4.0.4 on 2022-07-17 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0002_createtopicrequest'),
        ('tenants', '0023_tenant_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='block_chain_request',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s', to='blockchain.blockchainrequest'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='topic_id',
            field=models.CharField(blank=True, default='0.0.47654162', max_length=16, null=True, verbose_name='Hedera Topic ID'),
        ),
    ]
