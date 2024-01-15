# Generated by Django 4.0.4 on 2022-07-23 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0022_template_index_column_alter_templatefieldtype_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatefieldtype',
            name='type',
            field=models.IntegerField(choices=[(51, 'Primary Key'), (101, 'String'), (111, 'Integer'), (121, 'Float'), (131, 'Date'), (141, 'Phone'), (151, 'Email')], default=101, verbose_name='Field Type'),
        ),
    ]