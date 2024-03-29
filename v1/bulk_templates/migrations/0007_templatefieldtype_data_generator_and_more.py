# Generated by Django 4.0.4 on 2022-06-16 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0006_rename_farmers_added_bulkupload_actors_added_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatefieldtype',
            name='data_generator',
            field=models.IntegerField(blank=True, choices=[(101, 'Countries'), (201, 'Provinces'), (301, 'Producers')], default=None, null=True, verbose_name='Data Generator'),
        ),
        migrations.AlterField(
            model_name='templatefieldtype',
            name='type',
            field=models.IntegerField(choices=[(101, 'String'), (111, 'Integer'), (121, 'Float'), (131, 'Date'), (141, 'Phone'), (151, 'Email'), (161, 'Paragraph'), (171, 'Currency'), (181, 'Unit'), (191, 'Choice')], default=101, verbose_name='Field Type'),
        ),
    ]
