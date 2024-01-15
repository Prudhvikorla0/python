"""
Custom configuration for Excel types
"""
from sentry_sdk import capture_exception
from django.utils.translation import gettext_lazy as _
from utilities import functions as util_functions


class ConnectionTemplate(object):
    serializer = None

    @staticmethod
    def get_instance(data):
        from v1.nodes.models import Node
        if 'id' in data and data['id'] and data['id'] != "None":
            return Node.objects.get_by_encoded_id(data['id'])
        return None

    @staticmethod
    def get_serializer_class(instance):
        from v1.supply_chains.serializers.connections import ConnectNodeSerializer
        from v1.nodes.serializers.node import NodeSerializer
        if instance:
            return NodeSerializer
        return ConnectNodeSerializer

    @staticmethod
    def data(tenant, node, supply_chain, **kwargs):
        """
        Gets producers as queryset to pre-populate Excel sheet.
        """
        from v1.nodes.constants import NodeType, NodeStatus
        producers = node.get_connections(
            supply_chain=supply_chain).filter(
                type=NodeType.PRODUCER, status=NodeStatus.INACTIVE).distinct(
                    'created_on').order_by('created_on')
        return [
            {
                'id': i.idencode,
                'operation': i.operation.name if i.operation else "",
                'name': i.name,
                'house_name': i.house_name,
                'street': i.street,
                'city': i.city,
                'trace_code': i.trace_code,
                'registration_no': i.registration_no,
                'contact_name': i.contact_name,
                'email': i.email,
                'phone': i.phone,
                'country': i.country.name if i.country else "",
                'province': i.province.name if i.province else "",

            } for i in producers
        ]

    def validate(self, data, tenant, node, supply_chain, **kwargs):
        valid = True
        from v1.tenants.models import Country, Province
        for item in data:
            item['is_duplicate'] = False
            if 'country' not in item['data'] or not item['data']['country']['value']:
                continue
            if 'province' not in item['data'] or not item['data']['province']['value']:
                continue
            country = Country.objects.get_by_encoded_id(item['data']['country']['value'])
            province = Province.objects.get_by_encoded_id(item['data']['province']['value'])
            if province not in country.provinces.all():
                item['data']['province']['is_valid'] = False
                item['data']['province']['message'] = _('Province not part of selected country.')
                item['is_valid'] = False
            if data.count(item) > 1:
                valid = False
                item['is_valid'] = False
                item['message'] += _('Possible double entry in Excel. ')
                item['is_duplicate'] = True

        return data, valid

    def customize_file(self, template):
        pass

    def annotate_extras(self, data):
        from v1.nodes import constants as node_constants
        data['type'] = node_constants.NodeType.PRODUCER
        return data


class TransactionTemplate(object):

    serializer = None

    @staticmethod
    def get_instance(data):
        return None

    @staticmethod
    def get_serializer_class(instance):
        from v1.transactions.serializers.external import ExternalTransactionSerializer
        return ExternalTransactionSerializer

    @staticmethod
    def data(tenant, node, supply_chain, **kwargs):
        """
        Returns empty list
        """
        return []

    def validate(self, data, tenant, node, supply_chain, **kwargs):
        valid = True
        from v1.transactions.models import ExternalTransaction
        dup_check = []
        for item in data:
            td = {k: v['value'] for k, v in item['data'].items()}
            force_create = td.get('force_create', False)
            try:
                item['is_duplicate'] = False
                # Checking for double entry in the sheet
                if dup_check.count(td) > 0 and not force_create:
                    valid = False
                    item['is_valid'] = False
                    item['message'] += _('Possible double entry in Excel. ')
                    item['is_duplicate'] = True

                if item['is_valid']:
                    # Checking if similar transaction exists in the system.
                    transactions = ExternalTransaction.objects.filter(
                        source__encoded=td['node'], destination=node,
                        price=td['price'], unit__encoded=td['unit'],
                        destination_quantity=td['quantity'],
                        result_batches__product__encoded=td['product'],
                        date=util_functions.read_date(td['date']))
                    if transactions.exists() and not force_create:
                        valid = False
                        item['is_valid'] = False
                        item['message'] += _('Similar transaction already exists. Possible duplicate. ')
                        item['is_duplicate'] = True
            except Exception as e:
                capture_exception(e)
                item['is_duplicate'] = False
                item['is_valid'] = False
                item['message'] += _('Something went wrong. Please contact the admin. ')
            dup_check.append(td)

        return data, valid

    def customize_file(self, template):
        pass

    def annotate_extras(self, data):
        from v1.transactions import constants as transaction_constants
        data['type'] = transaction_constants.ExternalTransactionType.INCOMING
        return data



class QuestionnaireTemplate(object):

    serializer = None

    @staticmethod
    def get_instance(data):
        return None

    @staticmethod
    def get_serializer_class(instance):
        from v1.questionnaire.serializers import QuestionSerializer
        return QuestionSerializer

    @staticmethod
    def data(tenant, node, supply_chain, **kwargs):
        """
        Returns empty list
        """
        return []

    def validate(self, data, tenant, node, supply_chain, **kwargs):
        valid=True
        return data, valid

    def customize_file(self, template):
        pass

    def annotate_extras(self, data):
        return data
