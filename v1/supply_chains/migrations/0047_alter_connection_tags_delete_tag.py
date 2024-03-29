# Generated by Django 4.0.4 on 2023-11-22 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0052_auto_20231122_0722'),
        ('nodes', '0040_alter_nodedocument_tags'),
        ('questionnaire', '0005_alter_questionnaire_tags'),
        ('supply_chains', '0046_merge_20230918_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='tags',
            field=models.ManyToManyField(related_name='connections', to='tenants.tag', verbose_name='Connection Tags'),
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
