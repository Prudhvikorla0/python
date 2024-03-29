# Generated by Django 4.0.4 on 2022-05-16 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transactions', '0001_initial'),
        ('claims', '0001_initial'),
        ('products', '0002_batch_node'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dynamic_forms', '0002_initial'),
        ('supply_chains', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='verifiers',
            field=models.ManyToManyField(blank=True, related_name='claims', to='supply_chains.node', verbose_name='Verifiers'),
        ),
        migrations.AddField(
            model_name='attachedcriterion',
            name='creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachedcriterion',
            name='criterion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_criteria', to='claims.criterion', verbose_name='Criterion'),
        ),
        migrations.AddField(
            model_name='attachedcriterion',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_criterion', to='dynamic_forms.formsubmission', verbose_name='Extra Form Data'),
        ),
        migrations.AddField(
            model_name='attachedcriterion',
            name='updater',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='attached_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claims_attached', to='supply_chains.node', verbose_name='Claim Attached By'),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='claims.claim', verbose_name='Attached Claim'),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='updater',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='verifier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claim_verifications', to='supply_chains.node', verbose_name='Claim Verifier'),
        ),
        migrations.AddField(
            model_name='companycriterion',
            name='company_claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='criteria', to='claims.companyclaim', verbose_name='Criterion Attached Company Claim'),
        ),
        migrations.AddField(
            model_name='companyclaim',
            name='node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_claims', to='supply_chains.node'),
        ),
        migrations.AddField(
            model_name='batchcriterion',
            name='batch_claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='criteria', to='claims.batchclaim', verbose_name='Criterion Attached Batch Claim'),
        ),
        migrations.AddField(
            model_name='batchclaim',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='products.batch', verbose_name='Claim Attached Batch'),
        ),
        migrations.AddField(
            model_name='batchclaim',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='transactions.transaction', verbose_name='Transaction'),
        ),
    ]
