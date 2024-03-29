# Generated by Django 4.0.4 on 2022-09-14 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0043_transaction_rejection_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='rejection_reason',
            field=models.IntegerField(choices=[(101, 'Quality Issue'), (111, 'Data Issue'), (121, 'Other Reason')], default=None, verbose_name='Transaction Rejection Reason'),
        ),
    ]
