# Generated by Django 4.0.4 on 2022-07-21 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0030_alter_deliverynotification_expected_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='remaining_quantity',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=25, verbose_name='Remaining Quantity Of Product To Send'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='remaining_quantity_kg',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=25, verbose_name='Remaining Quantity Of Product To Send In KG'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=25, verbose_name='Quantity Of Product'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='quantity_kg',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=25, verbose_name='Quantity Of Product In KG'),
        ),
    ]
