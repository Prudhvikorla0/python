# Generated by Django 4.0.4 on 2023-11-03 06:21

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supply_chains', '0046_merge_20230918_0703'),
        ('nodes', '0037_nodedocument_expiry_date_nodedocument_synced_to_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Questionnaire Name')),
                ('description', models.TextField(blank=True, default='', null=True, verbose_name='Questionnaire Description')),
                ('submitter', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Questionnaire Submitted By')),
                ('submitted_date', models.DateField(default=datetime.date.today, verbose_name='Submitted Date')),
                ('status', models.IntegerField(choices=[(101, 'Generating Answers'), (111, 'Waiting For Approval'), (121, 'Approved')], default=101, verbose_name='Status Of Questionnaire')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Deleted')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='questionnaires', to='nodes.node', verbose_name='Questionnaire Owner')),
                ('tags', models.ManyToManyField(related_name='questionnaires', to='supply_chains.tag', verbose_name='Questionnaire Tags')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('question', models.TextField(blank=True, default='', null=True, verbose_name='Question')),
                ('synced_to', models.IntegerField(blank=True, choices=[(101, 'RO AI')], default=None, null=True, verbose_name='Question Synced To')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Deleted')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('questionnaire', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questionnaire.questionnaire', verbose_name='Questionnaire')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('answer', models.TextField(blank=True, default='', null=True, verbose_name='Answer')),
                ('synced_to', models.IntegerField(blank=True, choices=[(101, 'RO AI')], default=None, null=True, verbose_name='Answer Synced To')),
                ('type', models.IntegerField(blank=True, choices=[(101, 'RO AI')], default=None, null=True, verbose_name='Answer Synced To')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
                ('files', models.ManyToManyField(related_name='created_answers', to='nodes.nodedocument', verbose_name='Referred Documents')),
                ('question', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questionnaire.question', verbose_name='Answer')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
