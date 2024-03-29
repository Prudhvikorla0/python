# Generated by Django 4.0.4 on 2022-06-21 04:44

from django.db import migrations
from typing import List

from v1.bulk_templates import constants

transaction_fields = [
    {
        'required': True,
        'name': 'Source',
        'description': 'Source of the transaction.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'node',
        'data_generator': constants.DataGenerator.PRODUCERS,
        'column_pos': 'C',
        'width': 7,

    },
    {
        'required': True,
        'name': 'Product',
        'description': 'Product that is purchased.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'product',
        'data_generator': constants.DataGenerator.PRODUCTS,
        'column_pos': 'D',
        'width': 6,
    },
    {
        'required': True,
        'name': 'Quantity',
        'description': 'Total quantity of items purchased.',
        'type': constants.TemplateFieldTypes.FLOAT,
        'key': 'quantity',
        'data_generator': None,
        'column_pos': 'E',
        'width': 3,
    },
    {
        'required': True,
        'name': 'Unit',
        'description': 'Unit of quantity.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'unit',
        'data_generator': constants.DataGenerator.UNITS,
        'column_pos': 'F',
        'width': 3,
    },
    {
        'required': True,
        'name': 'Price',
        'description': 'Price paid for the transaction.',
        'type': constants.TemplateFieldTypes.FLOAT,
        'key': 'price',
        'data_generator': None,
        'column_pos': 'G',
        'width': 4,
    },
    {
        'required': True,
        'name': 'Currency',
        'description': 'Currency used for the transaction.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'currency',
        'data_generator': constants.DataGenerator.CURRENCIES,
        'column_pos': 'H',
        'width': 3,
    },
    {
        'required': True,
        'name': 'Transaction Date',
        'description': 'Date of the actual transaction.',
        'type': constants.TemplateFieldTypes.DATE,
        'key': 'date',
        'data_generator': None,
        'column_pos': 'I',
        'width': 5,
    },
]

node_fields = [
    {
        'required': False,
        'name': 'ID',
        'description': 'ID of Producer.',
        'type': constants.TemplateFieldTypes.PRIMARY_KEY,
        'key': 'id',
        'data_generator': None,
        'column_pos': 'C',
        'width': 5,
    },
    {
        'required': True,
        'name': 'Operation',
        'description': 'Operation of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'operation',
        'data_generator': constants.DataGenerator.OPERATIONS,
        'column_pos': 'D',
        'width': 5,
    },
    {
        'required': True,
        'name': 'Name',
        'description': 'Name of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'name',
        'data_generator': None,
        'column_pos': 'E',
        'width': 6,
    },
    {
        'required': False,
        'name': 'Registation Number',
        'description': 'Registation Number of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'registration_no',
        'data_generator': None,
        'column_pos': 'F',
        'width': 6,
    },
    {
        'required': False,
        'name': 'Email',
        'description': 'Email of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'email',
        'data_generator': None,
        'column_pos': 'G',
        'width': 7,
    },
    {
        'required': False,
        'name': 'Phone Number',
        'description': 'Phone Number of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'phone',
        'data_generator': None,
        'column_pos': 'H',
        'width': 6,
    },
    {
        'required': False,
        'name': 'Street Address',
        'description': 'Street Address of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'street',
        'data_generator': None,
        'column_pos': 'I',
        'width': 9,
    },
    {
        'required': False,
        'name': 'City',
        'description': 'City of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'city',
        'data_generator': None,
        'column_pos': 'J',
        'width': 6,
    },
    {
        'required': False,
        'name': 'Province',
        'description': 'Province of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'province',
        'data_generator': constants.DataGenerator.PROVINCES,
        'column_pos': 'K',
        'width': 6,
    },
    {
        'required': False,
        'name': 'Country',
        'description': 'Country of Producer.',
        'type': constants.TemplateFieldTypes.STRING,
        'key': 'country',
        'data_generator': constants.DataGenerator.COUNTRIES,
        'column_pos': 'L',
        'width': 7,
    },
]


def setup_template(apps: ..., fields: List[dict], template_type: int) -> object:
    """
    Function to create default template and add fields
    """
    Template = apps.get_model('bulk_templates', 'Template')
    TemplateFieldType = apps.get_model('bulk_templates', 'TemplateFieldType')
    TemplateField = apps.get_model('bulk_templates', 'TemplateField')
    if template_type == constants.TemplateType.CONNECTION:
        name = "Producers"
        description = "This is the default template to add Producers in bulk."
    else:
        name = "Transactions"
        description = "This is the default template to add Transactions in bulk."
    template, _ = Template.objects.get_or_create(
        type=template_type, is_default=True,
        tenant=None, defaults={'name': name, "description": description})

    for field_data in fields:
        column_pos = field_data.pop('column_pos')
        width = field_data.get('width')
        field, _ = TemplateFieldType.objects.get_or_create(
            key=field_data['key'], template_type=template_type,
            defaults=field_data)
        tf_data = {
                "column_pos": column_pos,
                "width": width,
            }
        temp_field, _ = TemplateField.objects.get_or_create(
            template=template, field=field, defaults=tf_data)
    return template


def add_template_field_types(apps, schema_editor):
    """
    This migration adds default field types for Bulk Templates for both
    connections and transactions.
    """
    try:
        setup_template(
            apps, node_fields, constants.TemplateType.CONNECTION)
        setup_template(
            apps, transaction_fields, constants.TemplateType.TRANSACTION)
    except:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_templates', '0007_rename_used_bulkupload_is_used_and_more'),
        ('bulk_templates', '0007_templatefieldtype_data_generator_and_more'),
    ]

    operations = [
        migrations.RunPython(add_template_field_types)
    ]
