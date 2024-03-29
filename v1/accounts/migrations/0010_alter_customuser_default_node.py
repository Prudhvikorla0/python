# Generated by Django 4.0.4 on 2022-06-01 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
        ('accounts', '0009_alter_customuser_default_node_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='default_node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_node_users', to='nodes.node', verbose_name='Default Node Of User'),
        ),
    ]
