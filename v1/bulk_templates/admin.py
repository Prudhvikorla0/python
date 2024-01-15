"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.bulk_templates import models as bulk_models


class TemplateAdmin(BaseAdmin):
    """ Customize Node documents admin """

    list_display = (
        'type', 'name', 'tenant', 'idencode'
    )


class TemplateFieldTypeAdmin(BaseAdmin):
    """ Customize Node documents admin """

    list_display = (
        'name', 'description', 'type', 'template_type', 'idencode'
    )


class TemplateFieldAdmin(BaseAdmin):
    """ Customize Node documents admin """

    list_display = (
        'template', 'field', 'column_pos', 'idencode'
    )


class BulkUploadAdmin(BaseAdmin):
    """ Customize Node documents admin """

    list_display = (
        'template', 'node', 'file', 'idencode',
        'total_new_items', 'new_items_completed', 'total_updations', 'updations_completed'
    )
    readonly_fields = BaseAdmin.readonly_fields + (
        'node', 'supply_chain', 'data', 'errors', 'validated_data')


admin.site.register(bulk_models.Template, TemplateAdmin)
admin.site.register(bulk_models.TemplateFieldType, TemplateFieldTypeAdmin)
admin.site.register(bulk_models.TemplateField, TemplateFieldAdmin)
admin.site.register(bulk_models.BulkUpload, BulkUploadAdmin)
