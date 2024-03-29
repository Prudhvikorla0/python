# Generated by Django 4.0.4 on 2022-06-25 21:40

from django.db import migrations, models
import functools
import utilities.function_generators


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0018_alter_nodemember_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='trace_code',
            field=models.CharField(blank=True, default=functools.partial(utilities.function_generators.formatter, *('RO{y}-{R10}',), **{}), max_length=500, null=True, verbose_name='Right Origins Traceability Code'),
        ),
    ]
