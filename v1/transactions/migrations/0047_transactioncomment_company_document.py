# Generated by Django 4.0.4 on 2022-11-03 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0028_node_upload_timestamp'),
        ('transactions', '0046_alter_transaction_rejection_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactioncomment',
            name='company_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='trans_document', to='nodes.nodedocument'),
        ),
    ]
