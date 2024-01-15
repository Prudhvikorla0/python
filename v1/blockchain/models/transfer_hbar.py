""" Custom Models for Creating Blockchain Transaction """
import json
from django.db import models
from django.conf import settings
from .. import library
from .. import constants

from .callback_auth import CallBackToken
from .request import BlockchainRequest

# Create your models here.


class TransferHBARRequest(BlockchainRequest):
    """ Model for transacting assets in the blockchain"""
    action = constants.ACTION_HBAR_TRANSFER

    def prepare_body(self):
        """ Over-ridden prepare_body to format body for the corresponding reques type """
        related_object = getattr(self, self.object_related_name.lower())
        body = super(TransferHBARRequest, self).prepare_body()

        params = {}
        params['receiver_id'] = related_object.receiver_id
        params['amount'] = related_object.recharge_amount
        body['params'] = params

        self.body = body
        self.save()
        return body

    def handle_response(self, response):
        """ Function implemented in the subclass to handle response format """
        related_object = getattr(self, self.object_related_name.lower())
        return related_object.update_hedera_data(response['data'])


class AbstractHBARTransaction(models.Model):
    """
    Abstract base class for Blockchain Transaction to be imported to corresponding
    model inside the project
    """

    block_chain_request = models.OneToOneField(
        BlockchainRequest, related_name='%(app_label)s_%(class)s', null=True, blank=True,
        default=None, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def initialize(self, user=None):
        """
        TransferAssetRequest is created and saves in block_chain_request,
        object_related_name is set accordingly
        """
        if not self.block_chain_request:
            token = CallBackToken.objects.create(creator=user)
            transfer_asset_request = TransferHBARRequest.objects.create(
                callback_token=token, creator=user,
                object_related_name=f"{self._meta.app_label}_{self.__class__.__name__}")
            self.block_chain_request = transfer_asset_request
            self.save()
        else:
            self.block_chain_request.callback_token.refresh()
        return self.block_chain_request

    def pre_check(self):
        if not self.block_chain_request:
            return True, "Pre-check success"
        if self.block_chain_request.is_delayed():
            self.block_chain_request.discard()
            return True, "Pre-check success"
        if self.block_chain_request.status != constants.BC_REQUEST_STATUS_PENDING:
            return True, "Pre-check success"
        return False, "Pending request already exists"

    def update_hedera_data(self, bc_hash):
        """ To be implemented in the subclass to update the blockchain hash """
        raise NotImplementedError()

    @property
    def sender_id(self):
        """ To be implemented in the subclass to  return the sender's public key """
        raise NotImplementedError()

    @property
    def sender_private(self):
        """ To be implemented in the subclass to return the sender's private """
        raise NotImplementedError()

    @property
    def receiver_id(self):
        """ To be implemented in the subclass to return the recipient's account id"""
        raise NotImplementedError()

    @property
    def recharge_amount(self):
        """
        To be implemented in the subclass to return quantity of
        item to be transacted
        """
        raise NotImplementedError()

    @property
    def initiator_wallet(self):
        """ To return wallet of the initiator to topup in case of low balance"""
        raise NotImplementedError()
