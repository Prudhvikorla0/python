# Generated by Django 4.0.4 on 2022-07-04 11:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0019_alter_currency_options_tenant_currencies'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tenantadmin',
            options={},
        ),
        migrations.AddField(
            model_name='tenant',
            name='blockchain_logging',
            field=models.BooleanField(default=False, verbose_name='Is Blockchain Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='ci_availability',
            field=models.IntegerField(choices=[(101, 'Fully Visible'), (111, 'Fully Anonymous'), (121, 'Node Managed Visible Default'), (131, 'Node Managed Anonymous Default')], default=101, verbose_name='Node Anonymity'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='ci_theming',
            field=models.BooleanField(default=False, verbose_name='Is Consumer Interface Theming Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='claim',
            field=models.BooleanField(default=True, verbose_name='Is Claim Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='custom_excel_template',
            field=models.BooleanField(default=False, verbose_name='Is Tenant Customized Excel Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='dashboard_theming',
            field=models.BooleanField(default=False, verbose_name='Is Dashboard Theming Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='dynamic_fields',
            field=models.BooleanField(default=False, verbose_name='Dynamic Fields Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='node_anonymity',
            field=models.IntegerField(choices=[(101, 'Fully Visible'), (111, 'Fully Anonymous'), (121, 'Node Managed Visible Default'), (131, 'Node Managed Anonymous Default')], default=101, verbose_name='Node Anonymity'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='purchase_order',
            field=models.BooleanField(default=True, verbose_name='Is Purchase Order Enabled'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='transaction',
            field=models.BooleanField(default=True, verbose_name='Is Transaction Enabled'),
        ),
        migrations.AlterUniqueTogether(
            name='tenantadmin',
            unique_together={('tenant', 'user')},
        ),
    ]
