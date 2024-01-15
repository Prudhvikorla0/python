"""Views in tracker app"""

from rest_framework import generics

from v1.tracker.serializers import tracker as tracker_serializers

from v1.products import models as prod_models

from v1.tracker.operations import BatchSelection

from v1.nodes import constants as node_consts
from v1.transactions import models as txn_models

from base import response


class TrackBatchFlowView(generics.RetrieveAPIView):
    """
    View lists preceeding transactions and related info of a batch
    """

    serializer_class = tracker_serializers.BatchTrackSerializer
    queryset = prod_models.Batch.objects.all()

    def get_object(self):
        """
        """
        id = self.kwargs['pk']
        try:
            return txn_models.SourceBatch.objects.get(id=id).batch
        except:
            return prod_models.Batch.objects.get(id=id)


class BatchDetailView(generics.RetrieveAPIView):
    """
    View details information about a stock.
    """

    serializer_class = tracker_serializers.BatchSerializer
    queryset = prod_models.Batch.objects.all()


class TrackerInfoView(generics.ListAPIView):
    """
    """
    serializer_class = tracker_serializers.TrackerInfoSerializer


    def get_queryset(self):
        """
        """
        batch = prod_models.Batch.objects.get(id=self.kwargs['pk'])
        batches,__ = BatchSelection().track_batches(
            batch=batch, base_batch=True, external=True)
        batches = prod_models.Batch.objects.filter(id__in=batches).exclude(
            node=None).select_related('node', 'node__province__country').order_by('id')
        return batches

    def list(self, request, *args, **kwargs):
        """
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {}
        ordered_query = queryset.order_by('node__id').distinct('node__id')
        countries = ordered_query.distinct('id').order_by('id').values_list(
        'node__province__country__name', flat=True)
        data['summary'] = {
            "countries": list(countries), 
            "actors": ordered_query.filter(
                node__type=node_consts.NodeType.COMPANY).count(), 
            "farmers": ordered_query.filter(
                node__type=node_consts.NodeType.PRODUCER).count()
        }
        data['map_data'] = serializer.data
        return response.SuccessResponse(data)
