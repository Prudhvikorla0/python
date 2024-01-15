# Generated by Django 4.0.4 on 2022-05-18 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_alter_tenantadmin_tenant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Country Name')),
                ('latitude', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Longitude')),
                ('code', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Country Code')),
                ('dial_code', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Dial Code')),
                ('provinces', models.JSONField(default=list)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='countries', to='tenants.tenant', verbose_name='Tenant')),
            ],
        ),
    ]
