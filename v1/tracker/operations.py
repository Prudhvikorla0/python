from v1.products.models import Batch
from v1.transactions import models as txn_models
from v1.transactions import constants as txn_consts


class BatchSelection:
    """
    """

    def __init__(self):
        """
        """
        self.tracked_batches = []
        self.untracked_batches = None
        self.source_batches = txn_models.SourceBatch.objects.none()

    def track_batches(self, batch=None, base_batch=False, external=False):
        """
        """
        if base_batch:
            self.untracked_batches = Batch.objects.filter(id=batch.id)
        try:
            txn = batch.incoming_transactions.first()
            self.untracked_batches |= txn.source_batches.all()
            self.source_batches |= txn.source_batch_objects.all()
        except:
            pass
        if batch not in self.tracked_batches:
            if external:
                internal_transaction = txn_models.InternalTransaction.objects.filter(
                    source_batches=batch)
                if not internal_transaction:
                    self.tracked_batches.append(batch.id)
            else:
                self.tracked_batches.append(batch.id)
        self.untracked_batches = self.untracked_batches.exclude(
            id=batch.id)
        if self.untracked_batches:
            self.track_batches(self.untracked_batches.first(), external=external)
        if external:
            self.source_batches = self.source_batches.exclude(
                transaction__transaction_type=txn_consts.TransactionType.INTERNAL
                ).exclude(transaction__externaltransaction__type=txn_consts.ExternalTransactionType.REVERSAL)
        return self.tracked_batches, self.source_batches.distinct()
