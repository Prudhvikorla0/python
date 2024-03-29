# Generated by Django 4.0.4 on 2022-06-08 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0016_supplychain'),
        ('claims', '0024_alter_attachedclaim_claim_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='supply_chains',
            field=models.ManyToManyField(blank=True, related_name='included_claims', to='supply_chains.supplychain', verbose_name='Supply Chains'),
        ),
    ]
