# Generated by Django 4.0.4 on 2022-05-16 19:09

import common.library
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('type', models.IntegerField(choices=[(101, 'Node Form'), (111, 'Node Member Form'), (121, 'Transaction Form'), (131, 'Claim Form'), (141, 'Connection Form'), (151, 'Transaction Enquiry Form')], default=101, verbose_name='Form Type')),
                ('version', models.IntegerField(blank=True, default=1, null=True, verbose_name='Form Version')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('type', models.IntegerField(choices=[(101, 'Text'), (111, 'Paragraph'), (121, 'Check-Box'), (131, 'Radio Button'), (141, 'Drop Down'), (151, 'File'), (161, 'Date')], default=101, verbose_name='Field Type')),
                ('heading', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Heading')),
                ('description', models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Description')),
                ('key', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Key')),
                ('postion', models.IntegerField(blank=True, default=1, null=True, verbose_name='Position')),
                ('required', models.BooleanField(default=False, verbose_name='Is Field Required')),
                ('options', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormFieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Value')),
                ('file', models.FileField(blank=True, default=None, max_length=500, null=True, upload_to=common.library._get_file_path)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_forms', to='dynamic_forms.form', verbose_name='Form')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]