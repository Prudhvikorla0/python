# Generated by Django 4.0.4 on 2022-09-14 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0044_alter_transaction_rejection_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='rejection_reason',
            field=models.IntegerField(blank=True, choices=[(101, 'Quality Issue'), (111, 'Data Issue'), (121, 'Other Reason')], default=None, null=True, verbose_name='Transaction Rejection Reason'),
        ),
    ]
