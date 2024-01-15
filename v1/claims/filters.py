"""Filters used in the claim apis."""

from django_filters import rest_framework as filters

from django.db.models import Q

from common.drf_custom import filters as custom_filters

from base import session

from utilities.functions import decode, decode_list

from v1.claims import constants as claim_constants
from v1.claims import models as claim_models

from v1.nodes import models as node_models

from v1.transactions import constants as txn_consts
from v1.transactions import models as txn_models

from v1.products import models as prod_models

class ClaimFilter(filters.FilterSet):
    """
    Filterclass claim.
    """
    supply_chain = filters.CharFilter(method='supply_chain_filter')
    verifier = filters.CharFilter(method='verifier_filter')
    type = filters.NumberFilter(method='type_filter')
    group = filters.NumberFilter(method='group_filter')
    node_claim = filters.BooleanFilter(field_name='attach_to_node')
    batch_claim = filters.BooleanFilter(field_name='attach_to_batch')
    transaction_attachment = filters.BooleanFilter(
        field_name='attach_while_transacting')
    connection_attachment = filters.BooleanFilter(
        field_name='attach_while_connecting')
    node_profile_attachment = filters.BooleanFilter(
        field_name='attach_from_profile')
    batch_detail_attachment = filters.BooleanFilter(
        field_name='attach_from_batch_details')
    operation = filters.CharFilter(method='operation_filter')
    product_type = filters.CharFilter(method='product_type_filter')
    main_txn_type = filters.CharFilter(method='main_txn_type_filter')
    child_txn_type = filters.CharFilter(method='child_txn_type_filter')
    country = filters.CharFilter(method='country_filter')
    node = filters.CharFilter(method='node_filter')
    batch = filters.CharFilter(method='batch_filter')
    transaction = filters.CharFilter(method='transaction_filter')
    product = filters.CharFilter(method='product_filter')
    

    class Meta:
        """
        Meta Info.
        """
        model = claim_models.Claim
        fields = ('supply_chain', 'verifier', 'type', 'node_claim', 
            'batch_claim', 'transaction_attachment', 'connection_attachment', 
            'node_profile_attachment', 'batch_detail_attachment', 
            'product_type', 'operation', 'main_txn_type', 'main_txn_type', 
            'operation', 'country', 'node', 'batch', 'transaction', 'group',
            'product',)

    def supply_chain_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        supply_chain_id = decode(value)
        query = Q(supply_chains__id=supply_chain_id)
        return queryset.filter(query)

    def verifier_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        verifier_id = decode(value)
        query = Q(verifiers__id=verifier_id)
        return queryset.filter(query)

    def type_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        if value == claim_constants.ClaimAttachedTo.BATCH:
            return queryset.filter(attach_to_batch=True)
        if value == claim_constants.ClaimAttachedTo.NODE:
            return queryset.filter(attach_to_node=True)
        if value == claim_constants.ClaimAttachedTo.CONNECTION:
            return queryset.filter(attach_while_connecting=True)
        return queryset
    
    def group_filter(self, queryset, name, value):
        """
        Search filter on the basis of group.
        """
        if value:
            return queryset.filter(group=value)
        return queryset
    
    def product_type_filter(self, queryset, name, value):
        """
        filter on the basis of product type.
        """
        if value:
            query = Q(product_types__id=decode(value))
            return queryset.filter(query)
        return queryset
    
    def product_filter(self, queryset, name, value):
        """
        filter on the basis of product_type from product.
        """
        if value:
            prod_ids = decode_list(value.split(","))
            product_types = list(prod_models.Product.objects.filter(
                id__in=prod_ids).values_list('product_type',flat=True))
            query = Q(product_types__in=product_types) | Q(product_types=None)
            return queryset.filter(query).distinct()
        return queryset
    
    def operation_filter(self, queryset, name, value):
        """
        filter on the basis of operators.
        """
        if value:
            query = Q(operations__id=decode(value))
            return queryset.filter(query).distinct()
        return queryset
    
    def main_txn_type_filter(self, queryset, name, value):
        """
        filter on the basis of main txn type.
        """
        if value:
            query = Q(txn_types__main_txn_type=value)
            return queryset.filter(query).distinct()
        return queryset
    
    def child_txn_type_filter(self, queryset, name, value):
        """
        filter on the basis of child txn type.
        """
        if value:
            query = Q(txn_types__child_txn_type=value)
            return queryset.filter(query).distinct()
        return queryset
    
    def node_filter(self, queryset, name, value):
        """
        filter on the basis of countries, operations
        by using the given txn.
        """
        if value:
            node = node_models.Node.get_by_encoded_id(
            value)
            current_node = session.get_current_node()
            query = Q(countries=node.country)
            if self.request.GET.get(
                'main_txn_type', None):
                main_txn = self.request.GET.get('main_txn_type')
                child_txn = self.request.GET.get('child_txn_type')
                if (main_txn == txn_consts.TransactionType.EXTERNAL) and (
                        child_txn == txn_consts.ExternalTransactionType.INCOMING):
                    query &= Q(operations=node.operation)
                else:
                    query &= Q(operations=current_node.operation)
            else:
                query &= Q(operations=current_node.operation)
            return queryset.filter(query).distinct()
        return queryset
    
    def country_filter(self, queryset, name, value):
        """
        filter on the basis of countries.
        """
        if value:
            query = Q(countries__id=decode(value))
            return queryset.filter(query).distinct()
        return queryset
    
    def batch_filter(self, queryset, name, value):
        """
        filter on the basis of product type, countries, operations and txn type
        by using given batch.
        """
        if value:
            batch = prod_models.Batch.get_by_encoded_id(value)
            node = batch.node
            query = Q(countries=node.country) & Q(operations=node.operation) & Q(
                product_types=batch.product.product_type
            )
            if batch.incoming_transactions.all():
                txn = batch.incoming_transactions.all().first()
                query &= Q(txn_types__main_txn_type=txn.transaction_type) & Q(
                    txn_types__child_txn_type=txn.child_transaction.type
                )
            return queryset.filter(query).distinct()
        return queryset
    
    def transaction_filter(self, queryset, name, value):
        """
        filter on the basis of product type, countries, operations and txn type
        by using the given txn.
        """
        if value:
            txn = txn_models.Transaction.get_by_encoded_id(value)
            product_types = list(txn.result_products().values_list(
                'product_type',flat=True))
            source_country = None
            operation = None
            if txn.source_node:
                source_country = txn.source_node.country
                operation = txn.source_node.operation
            dest_country = txn.destination_node.country if txn.destination_node else None
            operation = txn.source_node.operation if txn.source_node else None
            query = Q(countries=source_country) & Q(
                countries=dest_country) & Q(
                product_types__in=product_types) & Q(
                operations=operation) & Q(
                txn_types__main_txn_type=txn.transaction_type) & Q(
                    txn_types__child_txn_type=txn.child_transaction.type
                )
            return queryset.filter(query).distinct()
        return queryset


class VerificationFilter(filters.FilterSet):
    """
    Filter for Verifications.
    """

    supply_chain = filters.CharFilter(method='filter_supply_chain')
    claim = filters.CharFilter(method='filter_claim')
    assignee = filters.CharFilter(method='filter_assignee')
    type = filters.NumberFilter(method='filter_type')
    search = filters.CharFilter(method='search_fields')
    product = filters.CharFilter(method='filter_product')
    date_after = filters.DateFilter(
        field_name='created_on__date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_on__date', lookup_expr='lte')

    class Meta:
        model = claim_models.AttachedClaim
        fields = [
            'status', 'claim', 'assignee', 'verifier', 'product', 
            'supply_chain','search', 'type', 'date_after', 'date_before',
            ]

    def filter_supply_chain(self, queryset, name, value):
        query = Q(claim__supply_chains__id=decode(value))
        return queryset.filter(query)

    def filter_claim(self, queryset, name, value):
        query = Q(claim__id=decode(value))
        return queryset.filter(query)

    def filter_assignee(self, queryset, name, value):
        query = Q(attached_by__id=decode(value))
        return queryset.filter(query)

    def filter_verifier(self, queryset, name, value):
        query = Q(verifier__id=decode(value))
        return queryset.filter(query)

    def filter_type(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        if value == claim_constants.ClaimAttachedTo.BATCH:
            return queryset.filter(claim__attach_to_batch=True)
        if value == claim_constants.ClaimAttachedTo.NODE:
            return queryset.filter(claim__attach_to_node=True)
        return queryset

    def search_fields(self, queryset, name, value):
        query =Q(attached_by__name__icontains=value) | Q(
            verifier__name__icontains=value) | Q(
            claim__name__icontains=value)
        return queryset.filter(query)

    def filter_product(self, queryset, name, value):
        query = Q(claim__product__id=decode(value))
        return queryset.filter(query)
