# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0022_alter_attachedclaim_claim_alter_batchclaim_batch_and_more'),
        ('dynamic_forms', '0004_alter_formfieldvalue_form'),
        ('supply_chains', '0008_operation_tenant_alter_node_form_and_more'),
        ('products', '0003_alter_unit_tenant'),
        ('transactions', '0005_alter_transaction_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='previous_transactions', to='transactions.transaction', verbose_name='Parent Transactions'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='result_batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incoming_transaction', to='products.batch', verbose_name='Transaction Result Batch'),
        ),
        migrations.AlterField(
            model_name='transactionenquiry',
            name='claims',
            field=models.ManyToManyField(related_name='requested_enquiries', to='claims.claim', verbose_name='Claims Needed'),
        ),
        migrations.AlterField(
            model_name='transactionenquiry',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_enquiry', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AlterField(
            model_name='transactionenquiry',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_enquiries', to='supply_chains.node', verbose_name='Receiver'),
        ),
        migrations.AlterField(
            model_name='transactionenquiry',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_enquiries', to='supply_chains.node', verbose_name='Sender'),
        ),
    ]
