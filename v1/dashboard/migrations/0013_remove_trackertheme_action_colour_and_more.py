# Generated by Django 4.0.4 on 2022-09-21 04:43

import common.library
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_alter_trackertheme_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trackertheme',
            name='action_colour',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='colour_map_background',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='colour_map_clustor',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='colour_map_marker',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='colour_map_marker_text',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='colour_map_selected',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='primary_colour_light',
        ),
        migrations.RemoveField(
            model_name='trackertheme',
            name='text_colour',
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='colour_background_alpha',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Background Colour Alpha'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='logo',
            field=models.FileField(blank=True, null=True, upload_to=common.library._get_file_path, verbose_name='Tracker Logo'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='shade_colour_alpha',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Shade Colour Alpha'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='shade_colour_beta',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Shade Colour Beta'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='shade_colour_gamma',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Shade Colour Gamma'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_alpha',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Alpha'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_beta',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Beta'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_delta',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Delta'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_gamma',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Gamma'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_primary',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Primary'),
        ),
        migrations.AddField(
            model_name='trackertheme',
            name='text_colour_secondary',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Text Colour Secondary'),
        ),
    ]
