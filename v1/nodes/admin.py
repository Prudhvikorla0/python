"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.nodes import models as node_models


class NodeMemberInline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = node_models.NodeMember
    extra = 0
    fields = ('user', 'tenant', 'type','is_active','default_supply_chain',)

class NodeAdmin(BaseAdmin):

    def get_queryset(self, request):
        """overrided to remove n+1 query issue."""
        return super().get_queryset(request).select_related(
            'submission_form', 'inviter_questionnaire', 'signup_questionnaire', 
            'env_data', 'soc_data', 'soc_data', 'gov_data', 'province', 'currency', 
            'incharge', 'tenant')
    
    list_display = ('name', 'idencode', 'type')
    list_filter = ('type', 'is_producer', 'is_verifier', 'tenant')
    search_fields = ['name']
    readonly_fields = BaseAdmin.readonly_fields + (
        'connect_id', 'trace_code', 'submission_form', 'inviter_questionnaire', 
        'signup_questionnaire', 'env_data', 'soc_data', 'soc_data', 'gov_data'
    )
    inlines = [
        NodeMemberInline,
    ]


class NodeDocumentAdmin(BaseAdmin):
    list_display = ('name', 'idencode', )
    search_fields = ['name']


class NodeMemberAdmin(BaseAdmin):
    list_display = ('user', 'node', 'idencode',)
    list_filter = ('is_active', 'type','tenant')
    search_fields = ['user__first_name']

class FolderAdmin(BaseAdmin):
    list_display = ('name', 'node', 'idencode', )
    search_fields = ['name']


admin.site.register(node_models.Node, NodeAdmin)
admin.site.register(node_models.NodeDocument, NodeDocumentAdmin)
admin.site.register(node_models.NodeMember, NodeMemberAdmin)
admin.site.register(node_models.Folder,FolderAdmin)
