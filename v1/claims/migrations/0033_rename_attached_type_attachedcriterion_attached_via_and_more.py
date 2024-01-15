# Generated by Django 4.0.4 on 2022-08-09 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0032_alter_claim_description_alter_claim_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attachedcriterion',
            old_name='attached_type',
            new_name='attached_via',
        ),
        migrations.RemoveField(
            model_name='attachedclaim',
            name='attached_type',
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='attached_to',
            field=models.IntegerField(choices=[(101, 'Batch'), (111, 'Company')], default=101, verbose_name='Claim Attached to'),
        ),
        migrations.AddField(
            model_name='attachedclaim',
            name='attached_via',
            field=models.IntegerField(choices=[(101, 'Manual'), (111, 'Inheritance')], default=101, verbose_name='Attached Via'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_from_batch_details',
            field=models.BooleanField(default=True, verbose_name='Can claim be attached directly from batch details.(Relevant for product claims).'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_from_profile',
            field=models.BooleanField(default=True, verbose_name='Can claim be attached directly from profile.(Relevant for company claims).'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_to_batch',
            field=models.BooleanField(default=True, verbose_name='Can claim be attached to companies? (Formerly Company claims)'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_to_node',
            field=models.BooleanField(default=True, verbose_name='Can claim be attached to nodes? (Formerly Product claims)'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_while_connecting',
            field=models.BooleanField(default=False, verbose_name='Can claim be attached while adding connection(Relevant for company claims).'),
        ),
        migrations.AddField(
            model_name='claim',
            name='attach_while_transacting',
            field=models.BooleanField(default=True, verbose_name='Can claim be attached during transaction.(Relevant for product claims).'),
        ),
        migrations.AlterField(
            model_name='attachedclaim',
            name='claim',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='attached_claims', to='claims.claim', verbose_name='Attached Claim'),
            preserve_default=False,
        ),
    ]
