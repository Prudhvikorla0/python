# Generated by Django 4.0.4 on 2023-01-03 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskscore',
            name='environment',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='riskscore',
            name='governance',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='riskscore',
            name='overall',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='riskscore',
            name='social',
            field=models.FloatField(default=0.0),
        ),
    ]
