from .models import Form, FormField, FieldValueOption
from .serializers.form import FormSerializer

import json 

def get_form_fields(form_id):
    """Function to get fields of form in json format."""
    form = Form.get_by_encoded_id(form_id)
    fields = FormSerializer(form).data
    return json.dumps(list(
        fields['fields'])).replace('true', 'True').replace('false','False').replace('null', '""')

def add_form_and_fields(type,fields):
    """
    Function to create form with the given type and add fields into the form.
    fields should be list of dict. form.
    """
    form = Form.objects.create(type=type)
    for field in fields:
        field['form'] = form
        options = field.pop('options', None)
        field.pop('field', None)
        new_field = FormField.objects.create(**field)
        if options:
            new_options = []
            for option in options:
                option.pop('id', None)
                new_option = FieldValueOption.objects.create(**option)
                new_options.append(new_option)
            new_field.options.add(*new_options)
