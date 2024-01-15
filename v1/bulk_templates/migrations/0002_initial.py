# Generated by Django 4.0.4 on 2022-05-16 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bulk_templates', '0001_initial'),
        ('supply_chains', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkupload',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bulk_uploads', to='supply_chains.node', verbose_name='Node'),
        ),
        migrations.AddField(
            model_name='bulkupload',
            name='template',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_template', to='bulk_templates.template', verbose_name='Template'),
        ),
        migrations.AddField(
            model_name='bulkupload',
            name='updater',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='templatefieldtype',
            unique_together={('name', 'key')},
        ),
    ]