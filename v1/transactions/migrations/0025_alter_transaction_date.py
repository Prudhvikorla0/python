# Generated by Django 4.0.4 on 2022-07-13 19:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0024_transaction_message_hash_transaction_message_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(default=datetime.datetime.today, verbose_name='Transaction Date'),
        ),
    ]
