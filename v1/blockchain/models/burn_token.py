""" Custom Models for Wiping Asset. Representation for deleting asset """
import json
from django.db import models
from django.conf import settings
from .. import library
from .. import constants

from .callback_auth import CallBackToken
from .request import BlockchainRequest

# Create your models here.


class BurnTokenRequest(BlockchainRequest):
    """ Model for transacting assets in the blockchain"""
    action = constants.ACTION_TOKEN_TRANSFER

    def prepare_header(self, private=None, public=None):
        """ When doing a transaction, the header is signed using the owner's key and private """
        related_object = getattr(self, self.object_related_name.lower())
        header = super(BurnTokenRequest, self).prepare_header(
            public=related_object.owner_id,
            private=related_object.owner_private)
        return header

    def prepare_body(self):
        """ Over-ridden prepare_body to format body for the corresponding reques type """
        related_object = getattr(self, self.object_related_name.lower())
        body = super(BurnTokenRequest, self).prepare_body()

        params = {}
        params['receiver_id'] = settings.TREASURY_ACCOUNT_ID
        params['amount'] = int(related_object.quantity_to_burn)
        params['token_id'] = related_object.token_id

        body['params'] = params

        self.body = body
        self.save()
        return body

    def handle_response(self, response):
        """ Function implemented in the subclass to handle response format """
        related_object = getattr(self, self.object_related_name.lower())
        return related_object.update_hedera_data(response)


class AbstractBurnedToken(models.Model):
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
        BurnTokenRequest is created and saves in block_chain_request,
        object_related_name is set accordingly
        """
        if not self.block_chain_request:
            token = CallBackToken.objects.create(creator=user)
            burn_asset_request = BurnTokenRequest.objects.create(
                callback_token=token, creator=user,
                object_related_name=f"{self._meta.app_label}_{self.__class__.__name__}")
            self.block_chain_request = burn_asset_request
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
        """ To be implemented in the subclass to update hash when callback is received """
        raise NotImplementedError()

    @property
    def owner_id(self):
        """ To be implemented in the subclass to return owner's public key """
        raise NotImplementedError()

    @property
    def initiator_wallet(self):
        """ To return wallet of the initiator to topup in case of low balance"""
        raise NotImplementedError()

    @property
    def owner_private(self):
        """ To be implemented in the subclass to return owner's private """
        raise NotImplementedError()

    @property
    def quantity_to_burn(self):
        """ To be implemented in the subclass to return quantity to burn """
        raise NotImplementedError()

    @property
    def token_id(self):
        """ To be implemented in the subclass to return asset code of item to be burnd """
        raise NotImplementedError()
