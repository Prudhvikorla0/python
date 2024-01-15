# Generated by Django 4.0.4 on 2022-05-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0008_operation_tenant_alter_node_form_and_more'),
        ('products', '0003_alter_unit_tenant'),
        ('transactions', '0005_alter_transaction_status'),
        ('claims', '0021_alter_claim_reference_alter_criterion_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachedclaim',
            name='claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_claims', to='claims.claim', verbose_name='Attached Claim'),
        ),
        migrations.AlterField(
            model_name='batchclaim',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_claims', to='products.batch', verbose_name='Claim Attached Batch'),
        ),
        migrations.AlterField(
            model_name='batchclaim',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_claims', to='transactions.transaction', verbose_name='Transaction'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='reference',
            field=models.CharField(default='', max_length=16, verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='supply_chains',
            field=models.ManyToManyField(blank=True, related_name='included_claims', to='products.supplychain', verbose_name='Supply Chains'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='verifiers',
            field=models.ManyToManyField(blank=True, related_name='verifiable_claims', to='supply_chains.node', verbose_name='Verifiers'),
        ),
        migrations.AlterField(
            model_name='companyclaim',
            name='node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_claims', to='supply_chains.node', verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='criterion',
            name='reference',
            field=models.CharField(default='', max_length=16, verbose_name='Reference Number'),
        ),
    ]
