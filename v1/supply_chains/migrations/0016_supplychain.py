# Generated by Django 4.0.4 on 2022-06-08 22:37

import common.library
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0015_alter_province_country_alter_tenantadmin_tenant_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supply_chains', '0015_alter_tag_tenant'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplyChain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Supplychain')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to=common.library._get_file_path, verbose_name='Photo')),
                ('description', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Description')),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supply_chains', to='tenants.tenant', verbose_name='Tenant')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]