# Generated by Django 4.0.4 on 2022-06-15 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0010_rename_form_node_submission_form_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='number',
            field=models.PositiveIntegerField(default=1000),
            preserve_default=False,
        ),
    ]
