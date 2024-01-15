# Generated by Django 4.0.4 on 2022-06-02 22:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0010_tenant_subdomain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='provinces',
        ),
        migrations.RemoveField(
            model_name='country',
            name='tenant',
        ),
        migrations.AddField(
            model_name='tenant',
            name='countries',
            field=models.ManyToManyField(related_name='tenants', to='tenants.country', verbose_name='Country List'),
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Province Name')),
                ('latitude', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Longitude')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provinces', to='tenants.country', verbose_name='Country')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]