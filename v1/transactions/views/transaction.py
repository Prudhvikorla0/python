"""View for transaction related apis."""
from django.utils.translation import gettext_lazy as _
from django.db.models import Q,F
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics

from base.views import IdDecodeModelViewSet
from base import exceptions
from base import session
from base.response import SuccessResponse


from utilities.functions import decode

from v1.nodes.models import Node

from v1.transactions.serializers import transaction as txn_serializers
from v1.transactions import models as transaction_models
from v1.transactions.constants import ExternalTransactionType,TransactionType
from v1.transactions import filters as txn_filters
from v1.transactions.serializers import other as txn_extra_serializers

from v1.products.models import Unit

from v1.products.serializers import batch as batch_serializers


class TransactionCommentCreateListView(generics.ListCreateAPIView):
    """
    Viewset to create, list, update and delete claim comment.
    """

    serializer_class = txn_serializers.TransactionCommentSerializer

    def get_queryset(self):
        """
        Return comments with respect to the id passed in the queryparams.
        """
        txn_id = self.kwargs['id']
        comments = transaction_models.TransactionComment.objects.select_related(
            'creator').filter(transaction__id=txn_id).order_by(
            '-created_on')
        return comments


class TransactionCommentRetrieveView(generics.RetrieveDestroyAPIView):
    """
    Viewset to create, list, update and delete claim comment.
    """

    serializer_class = txn_serializers.TransactionCommentSerializer

    def get_object(self):
        """
        Return comments with respect to the id passed in the queryparams.
        """
        comment_id = self.kwargs['pk']
        try:
            comment = transaction_models.TransactionComment.objects.get(
                id=comment_id)
        except:
            raise exceptions.NotFound(_("Comment does not exist."))
        return comment

    def destroy(self, request, *args, **kwargs):
        """
        Destroy overrided to delete attached comment by checking 
        logged-in user's type. 
        """
        comment = self.get_object()
        member = session.get_current_node().node_members.get(
            user=session.get_current_user())
        if member != comment.member:
            raise exceptions.BadRequest(_("User can not remove the comment"))
        comment.delete()
        return SuccessResponse(_("Comment deleted successfully."))


class ValidateTransaction(APIView):
    """
    View to check transaction already exists or not.
    """

    def post(self, request, *args, **kwargs):
        """
        Post method is overrided.
        Checks the transaction already exists or not.
        """
        data = request.data
        current_node = session.get_current_node()
        node = None
        if data['type'] != ExternalTransactionType.INCOMING_WITHOUT_SOURCE:
            try:
                node = Node.objects.get(id=decode(data['node']))
            except:
                raise exceptions.BadRequest(_('Node does not exist.'))
        date = data['date']
        unit = Unit.objects.get(id=decode(data['unit']))
        source = current_node
        destination = node
        if data['type'] == ExternalTransactionType.INCOMING:
            source = node
            destination = current_node
        transactions = transaction_models.ExternalTransaction.objects.filter(
            source=source, destination=destination, price=data['price'], 
            destination_quantity=data['quantity'], unit=unit,
            result_batches__product__id=decode(data['product']), 
            date=date
        )
        if transactions.exists():
            data = {
                "is_exist": True,
                "transaction_id": transactions.first().number, 
                "message": _("Transaction already exists.")
            }
        else:
            data = {
                "is_exist": False,
                "message": _("Transaction does not exist.")
            }
        return SuccessResponse(data)


class TransactionBatchView(generics.RetrieveAPIView):
    """
    Api to lists batches under a transaction.
    For choosing between source and destionation batches
    here using source_batches=True and result_batches=True
    Parameters.
    """

    def get_object(self):
        """
        Return comments with respect to the id passed in the queryparams.
        """
        try:
            txn = transaction_models.Transaction.objects.get(
                id=self.kwargs['pk'])
        except:
            raise exceptions.NotFound(_("Transaction does not exist."))
        return txn
    
    def retrieve(self, request, *args, **kwargs):
        """
        Return batches under a specific txn based on the parameter given.
        """
        get_source_batches = eval(request.query_params.get(
            'source_batches', 'False').title())
        get_result_batches = eval(request.query_params.get(
            'result_batches', 'False').title())
        product = request.query_params.get('product', None)
        batches = {}
        txn = self.get_object()
        txn_source_batches = txn.source_batch_objects.all()
        txn_result_batches = txn.result_batches.all()
        source_batch_redirection = True
        result_batch_redirection = True
        if txn.transaction_type == TransactionType.EXTERNAL:
            source_batch_redirection = False
            result_batch_redirection = True
            if txn.child_transaction.source == session.get_current_node():
                source_batch_redirection = True
                result_batch_redirection = False
        if product:
            txn_source_batches = txn_source_batches.filter(
                batch__product__id=decode(product))
            txn_result_batches = txn_result_batches.filter(
                product__id=decode(product))
        if get_source_batches:
            source_batches = txn_extra_serializers.TxnSourceBatchSerializer(
                txn_source_batches,many=True).data
            batches['source_batches'] = source_batches
            batches['redirect'] = source_batch_redirection
        if get_result_batches:
            result_batches = txn_extra_serializers.TxnBatchSerializer(
                txn_result_batches,many=True).data
            batches['result_batches'] = result_batches
            batches['redirect'] = result_batch_redirection
        return SuccessResponse(batches)
