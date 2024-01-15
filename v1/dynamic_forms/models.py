"""Models of the app Dynamic Forms."""

from positions import PositionField

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import AbstractBaseModel
from common.library import _get_file_path

from v1.dynamic_forms import constants as dynamic_consts


class Form(AbstractBaseModel):
    """
    Model to store dynamic forms of each tenants.
    There are different dynamic form for each process like purchase order, 
    claim....

    Attribs:
        tenant(obj)     : tenant who holds the theme.
        type(int)       : form type. eg : node form, purchase order form...
        version(int)    : Version of the form.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    name = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Form Name'))
    description = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Form Description'))
    type = models.IntegerField(
        default=dynamic_consts.FormType.NODE_FORM, 
        choices=dynamic_consts.FormType.choices, 
        verbose_name=_('Form Type'))
    version = models.IntegerField(
        default=1, null=True, blank=True, verbose_name=_('Form Version'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.get_type_display()} - {self.name} - {self.idencode}'


class FieldValueOption(AbstractBaseModel):
    """
    Model to store values for dropdown fields.

    Attribs:
        name(char)     : option.
        is_defult(bool) : is this default option.
        is_active(int) : is this option available.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    name = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Option'))
    is_default = models.BooleanField(default=False, 
        verbose_name=_('Is Default Option'))
    is_active = models.BooleanField(default=True, 
        verbose_name=_('Is Option Active'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.idencode}'


class FormField(AbstractBaseModel):
    """
    Model stores fields under a each forms.

    Attribs:
        form(obj)        : form which holds the field.
        type(int)        : field type. eg : string, integer...
        heading(char)    : heading / name of the field.
        description(char): description about the field.
        key(char)        : unique key of the field.
        position(int)    : position of the field in the form.
        required(bool)   : is field value is required.
        options(json)    : field to save options if the field type is any 
            selection type.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, 
        related_name='fields', verbose_name=_('Form'))
    type = models.IntegerField(
        default=dynamic_consts.FieldType.TEXT, 
        choices=dynamic_consts.FieldType.choices, 
        verbose_name=_('Field Type'))
    label = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Label'))
    place_holder = models.CharField(
        max_length=2000, default='', null=True, blank=True, 
        verbose_name=_('Place Holder'))
    key = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Key'))
    position = PositionField(
        verbose_name=_('Position'), collection='form', default=1)
    required = models.BooleanField(
        default=False, verbose_name=_('Is Field Required'))
    options = models.ManyToManyField(
        FieldValueOption, related_name='fields', verbose_name=_('Options'), 
        blank=True)
    info = models.CharField(
        max_length=2000, default='', null=True, blank=True, 
        verbose_name=_('More Info'))
    width = models.IntegerField(
        choices=dynamic_consts.FieldWidth.choices, 
        default=dynamic_consts.FieldWidth.MEDIUM, 
        verbose_name=_('Field Width'))

    class Meta:
        """Meta Info."""
        unique_together = ['form', 'key',]
        ordering = ['position']

    def __str__(self):
        """Object name in django admin."""
        return f'{self.form} - {self.get_type_display()} - \
            {self.idencode}'


class FormSubmission(AbstractBaseModel):
    """
    Model to save forms for specific nodes.

    Attribs:
        node(obj)        : node which owns the submitted form.
        form(obj)        : form which holds the field.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, 
        related_name='submitted_forms', verbose_name=_('Form'))
    mongo_submission_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('MongoDB Form Submission Id'))
    
    def __str__(self):
        """Object name in django admin."""
        return f'{self.form} - {self.idencode}'

    def export_as_dict(self) -> dict:
        data = {}
        for value in self.field_values.all():
            key = value.field.key or value.field.label
            value = value.value or ', '.join(
                [i.name for i in value.selected_options.all()])
            data[key] = value
        return data


class FormFieldValue(AbstractBaseModel):
    """
    Model holds the field values submitted by the users.

    Attribs:
        form(obj)            : submission form.
        field(obj)           : field type of the value.
        value(char)          : field to save values from user except file type.
        file(file)           : field to save file type value from user.
        company_document(obj): company document object

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    form = models.ForeignKey(
        FormSubmission, on_delete=models.CASCADE, 
        related_name='field_values', verbose_name=_('Form'), 
        null=True, blank=True)
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('MongoDB Form Submission Id'))
    field = models.ForeignKey(
        FormField, on_delete=models.CASCADE, 
        related_name='values', verbose_name=_('Field'))
    value = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Value'))
    file = models.FileField(
        upload_to=_get_file_path,
        null=True, default=None, blank=True, max_length=500, 
        verbose_name=_('File'))
    selected_options = models.ManyToManyField(
        FieldValueOption, related_name='field_values', blank=True,
        verbose_name=_('Selected Options'))
    file_hash = models.CharField(
        max_length=2000, null=True, blank=True,
        verbose_name=_('File hash'))
    company_document = models.ForeignKey('nodes.NodeDocument', 
        on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        """Object name in django admin."""
        return f'{self.field} - {self.idencode}'
    
    @property
    def file_url(self):
        """Get file url name."""
        try:
            return self.file.url
        except:
            None

    def files(self):
        """
        Get file from company document if company document exists or else get 
        it from  file field 
        """
        if self.company_document:
            return self.company_document.file_url
        else:
            return self.file_url

    class Meta:
        ordering = ['field__position']
