"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.dynamic_forms import models as dynamic_models


class FieldInline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = dynamic_models.FormField
    extra = 0
    fields = (
        'type', 'label', 'place_holder', 'key', 'position', 
        'required', 'options', 'width'
              )

class FormAdmin(admin.ModelAdmin):
    """Class view to customize view of form."""

    list_display = ('version', 'type', 'idencode')
    inlines = [
        FieldInline,
    ]

class FormFieldAdmin(admin.ModelAdmin):
    """Class view to customize view of fields of form."""

    def get_queryset(self, request):
        """overrided to remove n+1 query issue."""
        return super().get_queryset(request).select_related('form')

    list_display = ('form', 'label', 'type', 'idencode')

class FormSubmissionAdmin(admin.ModelAdmin):
    """Class view to customize view of submission form."""

    def get_queryset(self, request):
        """overrided to remove n+1 query issue."""
        return super().get_queryset(request).select_related('form')

    list_display = ('form', 'idencode')

class FormFieldValueAdmin(admin.ModelAdmin):
    """Class view to customize view of form field value."""

    def get_queryset(self, request):
        """overrided to remove n+1 query issue."""
        return super().get_queryset(request).select_related(
            'form', 'field')

    list_display = ('form', 'field', 'idencode')

class FieldValueOptionAdmin(admin.ModelAdmin):
    """Class view to customize view of field value options."""

    list_display = ('name', 'idencode')

admin.site.register(dynamic_models.Form, FormAdmin)
admin.site.register(dynamic_models.FormField, FormFieldAdmin)
admin.site.register(dynamic_models.FormSubmission, FormSubmissionAdmin)
admin.site.register(dynamic_models.FormFieldValue, FormFieldValueAdmin)
admin.site.register(dynamic_models.FieldValueOption, FieldValueOptionAdmin)
