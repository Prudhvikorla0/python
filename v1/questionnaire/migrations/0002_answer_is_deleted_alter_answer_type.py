# Generated by Django 4.0.4 on 2023-11-03 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Is Deleted'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='type',
            field=models.IntegerField(blank=True, choices=[(101, 'Automatically Created'), (111, 'Manually Created'), (121, 'Automatic, Manually Updated')], default=101, null=True, verbose_name='Answer Synced To'),
        ),
    ]
