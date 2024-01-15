# Generated by Django 4.0.4 on 2023-09-29 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0049_country_score'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('consumer_interface', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CITheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Theme Name')),
                ('is_default', models.BooleanField(default=False, verbose_name='Is Default Theme')),
                ('primary_colour', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Primary Colour')),
                ('secondary_colour', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Secondary Colour')),
                ('background_colour_alpha', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Background Colour Alpha')),
                ('background_colour_beta', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Background Colour Beta')),
                ('text_colour_primary', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Primary')),
                ('text_colour_secondary', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Secondary')),
                ('text_colour_alpha', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Alpha')),
                ('text_colour_beta', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Beta')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ci_themes', to='tenants.tenant', verbose_name='Tenant')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
