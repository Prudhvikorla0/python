# Generated by Django 4.0.4 on 2022-05-16 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_alter_tenantadmin_tenant_alter_tenantadmin_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenantadmin',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_admins', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]