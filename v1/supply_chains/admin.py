"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.supply_chains import models as supply_models
from v1.supply_chains import graph_models as sc_graph_models


class OperationAdmin(BaseAdmin):
    list_display = ('name', 'node_type', 'idencode',)
    list_filter = ('tenant', )

    search_fields = ['name',]


class SupplyChainAdmin(BaseAdmin):
    list_display = ('name', 'idencode', 'tenant',)
    list_filter = ('tenant', 'is_active')

    search_fields = ['name']


class ConnectionAdmin(BaseAdmin):
    readonly_fields = BaseAdmin.readonly_fields + (
        'connection_pair', 'source', 'target',
        'supply_chain', 'tags', 'submission_form', 'invited_by'
    )
    list_display = ('source', 'target', 'idencode',)
    search_fields = ['source__name', 'target__name',]
    list_filter = ('tenant',)


class NodeSupplyChainAdmin(BaseAdmin):

    def delete_model(self, request, obj):
        """
        """
        graph_nodes = sc_graph_models.NodeGraphModel.nodes.filter(
            pg_node_sc_id=obj.id)
        for graph_node in graph_nodes:
            graph_node.disconnect_all()
            graph_node.delete()
        obj.delete()

    def delete_queryset(self, request, queryset):
        """
        """
        for node_sc in queryset:
            self.delete_model(request=request,obj=node_sc)

    list_display = ('node', 'supply_chain', 'idencode',)
    list_filter = ('supply_chain', 'is_active', 'node__tenant')

    search_fields = ['node__name', 'supply_chain__name']


admin.site.register(supply_models.Operation, OperationAdmin)
admin.site.register(supply_models.SupplyChain, SupplyChainAdmin)
admin.site.register(supply_models.Connection, ConnectionAdmin)
admin.site.register(supply_models.NodeSupplyChain, NodeSupplyChainAdmin)


from django_neomodel import admin as neo_admin
from .graph_models import NodeGraphModel as  NeoModel


# neo_admin.register(NeoModel, BookAdmin)