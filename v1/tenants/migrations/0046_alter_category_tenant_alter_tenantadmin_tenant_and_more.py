# Generated by Django 4.0.4 on 2023-07-05 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0045_tenant_connection_claim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='tenant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='tenants.tenant', verbose_name='Tenant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tenantadmin',
            name='tenant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='admins', to='tenants.tenant', verbose_name='Tenant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tenantadmin',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tenant_admin', to=settings.AUTH_USER_MODEL, verbose_name='Admin User'),
            preserve_default=False,
        ),
    ]