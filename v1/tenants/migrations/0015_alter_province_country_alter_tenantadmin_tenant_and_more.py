# Generated by Django 4.0.4 on 2022-06-08 05:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0014_tenant_claim_form_tenant_node_form_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='province',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='provinces', to='tenants.country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='tenantadmin',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admins', to='tenants.tenant', verbose_name='Tenant'),
        ),
        migrations.AlterField(
            model_name='tenantadmin',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tenant_admin', to=settings.AUTH_USER_MODEL, verbose_name='Admin User'),
        ),
    ]