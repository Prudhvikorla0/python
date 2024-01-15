# Generated by Django 4.0.4 on 2023-07-19 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0028_alter_formfield_form_alter_formfieldvalue_field_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='type',
            field=models.IntegerField(choices=[(101, 'Node Form'), (111, 'Node Member Form'), (121, 'Internal Transaction Form'), (122, 'External Transaction Form'), (131, 'Claim Form'), (141, 'Connection Form'), (151, 'Transaction Enquiry Form'), (161, 'Verifier Form')], default=101, verbose_name='Form Type'),
        ),
    ]
