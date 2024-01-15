# Generated by Django 4.0.4 on 2023-06-07 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0056_connectionclaim_alter_attachedclaim_attached_to_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='group',
            field=models.IntegerField(choices=[(101, 'Certification Claim'), (111, 'Document Claim'), (121, 'Self Assessment')], default=101, verbose_name='Claim Group'),
        ),
    ]
