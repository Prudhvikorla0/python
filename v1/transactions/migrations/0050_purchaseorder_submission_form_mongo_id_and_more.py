# Generated by Django 4.0.4 on 2023-05-26 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0049_alter_purchaseorder_submission_form_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='submission_form_mongo_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Extra Form Data Mongo Submission Id'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='submission_form_mongo_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Extra Form Data Mongo Submission Id'),
        ),
    ]
