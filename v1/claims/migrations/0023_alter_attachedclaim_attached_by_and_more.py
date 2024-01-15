# Generated by Django 4.0.4 on 2022-06-01 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
        ('claims', '0022_alter_attachedclaim_claim_alter_batchclaim_batch_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachedclaim',
            name='attached_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claims_attached', to='nodes.node', verbose_name='Claim Attached By'),
        ),
        migrations.AlterField(
            model_name='attachedclaim',
            name='verifier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claim_verifications', to='nodes.node', verbose_name='Claim Verifier'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='verifiers',
            field=models.ManyToManyField(blank=True, related_name='verifiable_claims', to='nodes.node', verbose_name='Verifiers'),
        ),
        migrations.AlterField(
            model_name='companyclaim',
            name='node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_claims', to='nodes.node', verbose_name='Company'),
        ),
    ]
