# Generated by Django 4.0.4 on 2023-10-06 10:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_batch_risk_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Batch Date'),
        ),
    ]
