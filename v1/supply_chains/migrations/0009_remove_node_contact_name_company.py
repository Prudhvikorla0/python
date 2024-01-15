# Generated by Django 4.0.4 on 2022-05-21 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supply_chains', '0008_operation_tenant_alter_node_form_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='contact_name',
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supply_chains.node')),
                ('incharge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
            bases=('supply_chains.node',),
        ),
    ]