# Generated by Django 4.0.4 on 2022-06-10 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0013_remove_formfield_options_fieldvalueoption_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfield',
            name='width',
            field=models.IntegerField(choices=[(101, 'Small'), (111, 'Medium'), (121, 'Large')], default=101, verbose_name='Field Width'),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='type',
            field=models.IntegerField(choices=[(101, 'Text'), (111, 'Number'), (121, 'Email'), (131, 'Check-Box'), (141, 'Paragraph'), (151, 'File'), (161, 'Date'), (171, 'Drop Down'), (181, 'Radio Button')], default=101, verbose_name='Field Type'),
        ),
    ]
