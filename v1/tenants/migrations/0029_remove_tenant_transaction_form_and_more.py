# Generated by Django 4.0.4 on 2022-08-10 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0020_alter_form_type'),
        ('tenants', '0028_remove_country_name_en_uk_remove_country_name_en_us_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='transaction_form',
        ),
        migrations.AddField(
            model_name='tenant',
            name='external_transaction_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='external_transaction_tenant', to='dynamic_forms.form', verbose_name='Extra Fields For External Transaction'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='internal_transaction_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='internal_transaction_tenant', to='dynamic_forms.form', verbose_name='Extra Fields For Internal Transaction'),
        ),
    ]