# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_alter_tenantadmin_tenant'),
        ('bulk_templates', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkupload',
            name='template',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_uploads', to='bulk_templates.template', verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='template',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excel_templates', to='tenants.tenant', verbose_name='Tenant'),
        ),
    ]
