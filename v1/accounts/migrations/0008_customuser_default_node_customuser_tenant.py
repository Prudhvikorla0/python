# Generated by Django 4.0.4 on 2022-05-27 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0013_alter_nodemember_user'),
        ('tenants', '0010_tenant_subdomain'),
        ('accounts', '0007_customuser_created_on_customuser_creator_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='default_node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='supply_chains.node', verbose_name='Default Node Of User'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]
