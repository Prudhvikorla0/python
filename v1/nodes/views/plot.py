# from rest_framework import generics
# from rest_framework import filters

# from base import session
# from base.views import IdDecodeModelViewSet

# from v1.nodes.serializers import plot as plot_serializers
# from v1.nodes import models as plot_models


# class NodePlotView(IdDecodeModelViewSet):
#     """
#     Api to create and list node plot.
#     """
#     http_method_names = ['get', 'post', 'patch',]
#     filter_backends = [filters.SearchFilter,]
#     search_fields = ['name',]
#     serializer_class = plot_serializers.NodePlotSerializer

#     def get_queryset(self):
#         """
#         Return plots of the current node.
#         """
#         node_plots = session.get_current_node().farm_locations.all()
#         return node_plots


# class PlotDocumentView(IdDecodeModelViewSet):
#     """
#     Api to create and list plot documents.
#     """
#     http_method_names = ['get', 'post', 'patch',]
#     filter_backends = [filters.SearchFilter,]
#     search_fields = ['name',]
#     serializer_class = plot_serializers.PlotDocumentSerializer

#     def get_queryset(self):
#         """
#         Return documents of the specified node plot..
#         """
#         node_plot = self.kwargs['id']
#         node_plots = plot_models.PlotDocument.objects.filter(
#             node_plot__id=node_plot)
#         return node_plots
