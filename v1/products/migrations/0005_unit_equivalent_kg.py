# Generated by Django 4.0.4 on 2022-06-02 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_batch_node'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='equivalent_kg',
            field=models.FloatField(blank=True, default=0.0, null=True, verbose_name='Unit Equivalent In Kilogram'),
        ),
    ]
