# Generated by Django 4.0.4 on 2022-06-30 03:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0021_deliverynotification_purchaseorder_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='purchase_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='transactions.purchaseorder', verbose_name='Attached Purchase Order'),
        ),
    ]