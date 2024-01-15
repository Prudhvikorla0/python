"""Serializers used for creating dashboard apis."""

from rest_framework import serializers
from django.db.models import Sum, Q, F, Count,Subquery, OuterRef
from django.db.models.functions import ExtractYear
from django.utils import timezone

from utilities.functions import decode, percentage, get_past_months, read_date, split_list

from base import exceptions
from base import session

from v1.nodes import models as node_models
from v1.nodes import constants as node_consts

from v1.supply_chains import models as supply_models
from v1.supply_chains import constants as supply_consts

from v1.claims import constants as claim_consts

from v1.products import models as prod_models

from v1.transactions import constants as txn_consts
from v1.transactions import models as txn_models

from v1.risk import models as risk_models
from v1.risk import constants as risk_consts

from v1.dashboard import constants as dashboard_consts


class ConnectionStatSerializer(serializers.ModelSerializer):
    """Serializer return statistical data about connections of a node."""

    connection_stats = serializers.SerializerMethodField()
    company_stats = serializers.SerializerMethodField()
    transaction_stats = serializers.SerializerMethodField()

    supply_chain = None

    class Meta:
        """Meta Info"""
        model = node_models.Node
        fields = ('connection_stats', 'company_stats', 'transaction_stats',)

    def __init__(self, *args, **kwargs):
        super(ConnectionStatSerializer, self).__init__(*args, **kwargs)
        try:
            sc_id = decode(self.context['request'].query_params.get(
                'supply_chain', None))
            self.supply_chain = supply_models.SupplyChain.objects.get(
                id=sc_id)
        except:
            pass

    def get_connection_stats(self, node):
        """Return numerical stats about connections of a node."""
        connections = node.get_connections(supply_chain=self.supply_chain).all()
        request = self.context['request']
        date1 = request.query_params.get('date1')
        date2 = request.query_params.get('date2')
        if date1:
            connections = connections.filter(
                created_on__date__range=[date1, date2])
        companies = connections.filter(type=node_consts.NodeType.COMPANY)
        producers = connections.filter(type=node_consts.NodeType.PRODUCER)

        transacted_connections = connections.filter(
            Q(outgoing_transactions__date__range=(date1, date2)) |
            Q(incoming_transactions__date__range=(date1, date2))
        ).distinct('id')
        transacted_companies = companies.filter(
            Q(outgoing_transactions__date__range=(date1, date2)) |
            Q(incoming_transactions__date__range=(date1, date2))
        ).distinct('id')
        transacted_producers = producers.filter(
            Q(outgoing_transactions__date__range=(date1, date2)) |
            Q(incoming_transactions__date__range=(date1, date2))
        ).distinct('id')
        connection_data = {
            "total": connections.count(),
            "companies": companies.count(),
            "producers": producers.count(),
            "active": connections.filter(
                target_connections__status=supply_consts.ConnectionStatus.APPROVED
            ).count(),
            "pending": connections.filter(
                target_connections__status=supply_consts.ConnectionStatus.PENDING
            ).count(),
            "transacted": transacted_connections.count(),
            "transacted_companies": transacted_companies.count(),
            "transacted_producers": transacted_producers.count(),
        }
        return connection_data

    def get_company_stats(self, company):
        """Return statistics of the company."""
        connections = company.source_connections.all()
        members = company.members.all()
        if self.supply_chain:
            connections = connections.filter(supply_chain=self.supply_chain)
        company_data = {
            "connections": connections.count(),
            "members": members.count(),
            "profile_completion": company.profile_completion
        }
        return company_data

    def get_transaction_stats(self, node):
        """Return statistics of the transaction."""
        node_transactions = node.incoming_transactions.all()

        request = self.context['request']
        date1 = request.query_params.get('date1')
        date2 = request.query_params.get('date2')
        if date1:
            node_transactions = node_transactions.filter(
                date__range=[date1, date2])

        received_stock = node_transactions.aggregate(
            Sum('destination_quantity'))['destination_quantity__sum']

        latest_transaction = node.incoming_transactions.all().order_by(
            'upload_timestamp').first()

        transaction_data = {
            "received_stock": received_stock if received_stock else 0,
            "upload_timestamp": latest_transaction.upload_timestamp if latest_transaction else None,
        }

        return transaction_data


class SupplierStatSerializer(serializers.ModelSerializer):
    """
    Serializer return statistical data about supplier connections of a node.
    """

    suppliers_stats = serializers.SerializerMethodField()
    company_stats = serializers.SerializerMethodField()
    product_stats = serializers.SerializerMethodField()
    supplier_type_stats = serializers.SerializerMethodField()
    location_stats = serializers.SerializerMethodField()
    supplier_tier_stats = serializers.SerializerMethodField()

    supply_chain = None
    suppliers = node_models.Node.objects.none()
    connections = node_models.Node.objects.none()

    class Meta:
        """Meta Info"""
        model = node_models.Node
        fields = (
            'suppliers_stats', 'company_stats', 'product_stats'
            ,'supplier_type_stats', 'location_stats','supplier_tier_stats',)

    def __init__(self, *args, **kwargs):
        super(SupplierStatSerializer, self).__init__(*args, **kwargs)
        try:
            sc_id = decode(self.context['request'].query_params.get(
                'supply_chain', None))
            self.supply_chain = supply_models.SupplyChain.objects.get(
                id=sc_id)
        except:
            pass
        self.suppliers = self.instance.get_connections(
                supply_chain=self.supply_chain).filter(is_supplier=True)
        self.connections = self.instance.get_connections(
            supply_chain=self.supply_chain)
        
    def get_t2_suppliers(self):
        """
        Return suppliers of the current nodes connections.
        """
        t2_suppliers = node_models.Node.objects.filter(
            target_connections__source__in=self.suppliers,
            target_connections__is_supplier=True,
            ).annotate(
            supply_chain_id=F('target_connections__supply_chain__id')
            )
        if self.supply_chain:
            t2_suppliers = t2_suppliers.filter(
                supply_chain_id=self.supply_chain.id)
        return t2_suppliers.distinct()

    def get_suppliers_stats(self, node):
        """Return numerical stats about supplier connections of a node."""
        t1_having_suppliers = node.get_t1_having_connections(
                sc=self.supply_chain, connections=self.suppliers).count()
        certificate_having_suppliers = self.suppliers.exclude(
            node_claims=None
            ).count()
        t2_suppliers  = self.get_t2_suppliers()
        active_t2_suppliers = t2_suppliers.filter(
            status=node_consts.NodeStatus.ACTIVE)
        countries = self.suppliers.order_by(
                'province__country__id'
                ).distinct('province__country__id')
        high_risk_countries = countries.filter(
                    province__country__score__lte=43)
        suppliers_data = {
            "total": self.suppliers.count(),
            "active": self.suppliers.filter(
                target_connections__status=supply_consts.ConnectionStatus.APPROVED
                ).count(),
            "suppliers_country_count": countries.count(),
            "high_risk_supplier_countries": percentage(
                high_risk_countries.count(),countries.count()),
            "t1_having_suppliers": t1_having_suppliers,
            "t1_having_suppliers_percentage": percentage(
                t1_having_suppliers,self.suppliers.count()), 
            "certificated_suppliers_percentage": percentage(
                certificate_having_suppliers,self.suppliers.count()),
            "t2_active_suppliers_percentage": percentage(
                active_t2_suppliers.count(),t2_suppliers.count())
        }
        return suppliers_data
    
    def get_product_stats(self, company):
        """
        return product related info in stock.
        """
        products = prod_models.Product.objects.all()
        if self.supply_chain:
            products = (products.filter(
                supply_chain=self.supply_chain, 
                batches__node=session.get_current_node(),
                batches__incoming_transactions__externaltransaction__destination=company
                ) | products.filter(
                supply_chain=self.supply_chain, 
                batches__node=session.get_current_node(),
                batches__current_quantity__gt=0)).distinct()
        txn_types = [
            txn_consts.ExternalTransactionType.INCOMING, 
            txn_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE, 
            txn_consts.ExternalTransactionType.OUTGOING
        ]
        product_info = []
        for product in products:
            txns = txn_models.ExternalTransaction.objects.filter(
                destination=company, 
                type__in=txn_types, 
                status=txn_consts.TransactionStatus.APPROVED,
                source_batches__product=product
            ).annotate(country=F('source__province__country__name'))
            # created_stock_quantity = prod_models.Batch.objects.filter(
            #     node=company, incoming_transactions=None, product=product
            #     ).aggregate(
            #         total_quantity=Sum('initial_quantity',default=0.0)
            #     )['total_quantity']
            # txn_stock_quantity = txns.aggregate(
            #     total_quantity=Sum('destination_quantity',default=0.0)
            #     )['total_quantity']
            batch_quantity = (prod_models.Batch.objects.filter(
                node=company, product=product,
                incoming_transactions__status=txn_consts.TransactionStatus.APPROVED
                ) | prod_models.Batch.objects.filter(
                node=company, product=product,
                incoming_transactions=None
                )).distinct().aggregate(total_quantity=Sum('current_quantity',default=0.0)
                )['total_quantity']
            product_data = {
                "name": product.name, 
                "suppliers": txns.filter(source__in=self.suppliers).order_by(
                    'source__id').distinct('source__id').count(), 
                "locations": txns.order_by(
                    'country').exclude(country=None).distinct('country'
                    ).values_list('country',flat=True),
                "quantity": batch_quantity,
                "unit": product.unit.name
            }
            product_info.append(product_data)
        return product_info
    
    def get_supplier_type_stats(self, company):
        """
        Supplier type based data.
        """
        suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('overall')[:1]))
        high_risk_suppliers = suppliers.filter(risk_score_value__lte=43)
        medium_risk_suplliers = suppliers.filter(
            risk_score_value__lte=60, risk_score_value__gt=43)
        low_risk_suppliers = suppliers.filter(risk_score_value__gt=60)
        operations = session.get_current_tenant().node_operations.annotate(
            node_count=Count('nodes',filter=Q(nodes__in=self.suppliers)),
            low_risk=Count('nodes', filter=Q(nodes__in=low_risk_suppliers)),
            medium_risk=Count('nodes', filter=Q(nodes__in=medium_risk_suplliers)),
            high_risk=Count('nodes', filter=Q(nodes__in=high_risk_suppliers))
        ).values('name','node_count','low_risk','medium_risk','high_risk')
        return operations
    
    def get_location_stats(self,company):
        """
        Return location wise suppliers info.
        """
        distinct_nodes = self.suppliers.filter(
            outgoing_transactions__destination=session.get_current_node()
            ).order_by(
            'province_id').distinct('province_id')
        location_data = []
        for distinct_node in distinct_nodes:
            province = distinct_node.province
            t1_suppliers = self.suppliers.filter(province=province)
            products = prod_models.Product.objects.filter(
                batches__incoming_transactions__externaltransaction__destination=company,
                batches__incoming_transactions__externaltransaction__source__in=t1_suppliers
                ).distinct().values_list('name',flat=True)
            info = {
                "province":province.name,
                "country": province.country.name,
                "country_risk": province.country.risk_level,
                "t1_suppliers": t1_suppliers.count(),
                "products": products
            }
            location_data.append(info)
        return location_data
    
    def get_company_stats(self, company):
        """Return statistics of the company."""
        company_data = {
            "connections": self.connections.count(),
            "profile_completion": company.profile_completion, 
            "certifications": company.node_claims.count()
        }
        return company_data
    
    def create_supplier_tier_data(self,suppliers=None,tier_info=[], total_suppliers=[]):
        """
        Method creates supplier tier data.
        """
        new_suppliers = node_models.Node.objects.none()
        added_suppliers = []
        for supplier in suppliers:
            suppliers = suppliers.exclude(id=supplier.id)
            if supplier in added_suppliers:
                tier_data = {
                    "tier": 0,
                    "total_suppliers": 0,
                    "low_risk_suppliers": 0,
                    "medium_risk_suppliers": 0,
                    "high_risk_suppliers": 0
                }
                return tier_data
            new_suppliers = new_suppliers | supplier.get_connections(
                supply_chain=self.supply_chain).filter(
                is_supplier=True).exclude(id__in=total_suppliers)
            added_suppliers.append(supplier)
            total_suppliers.append(supplier.id)
            if not suppliers and new_suppliers:
                new_suppliers = new_suppliers.distinct().annotate(
                    risk_score_value=Subquery(
                    risk_models.RiskScore.objects.filter(
                    node=OuterRef('pk')).order_by('-id').values('overall')[:1]))
                low_risk_suppliers = new_suppliers.filter(risk_score_value__gt=60)
                high_risk_suppliers = new_suppliers.filter(risk_score_value__lte=43)
                medium_risk_suplliers = new_suppliers.filter(
                    risk_score_value__lte=60, risk_score_value__gt=43)
                tier_data = {
                    "tier": len(tier_info)+1,
                    "total_suppliers": new_suppliers.count(),
                    "low_risk_suppliers": low_risk_suppliers.count(),
                    "medium_risk_suppliers": medium_risk_suplliers.count(),
                    "high_risk_suppliers": high_risk_suppliers.count()
                }
                tier_info.append(tier_data)
                suppliers = new_suppliers
                if suppliers:
                    self.create_supplier_tier_data(
                        suppliers,tier_info=tier_info,total_suppliers=total_suppliers)
                new_suppliers = node_models.Node.objects.none()
        return tier_info

    
    def get_supplier_tier_stats(self,company):
        """
        Return supplier tier wise statistics.
        """
        suppliers = node_models.Node.objects.filter(
            id=company.id)
        tier_info = self.create_supplier_tier_data(suppliers,tier_info=[],total_suppliers=[])
        return tier_info

    
class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Product Info.
    """

    batch_data = serializers.SerializerMethodField()

    class Meta:
        """
        Meta Info.
        """
        model = prod_models.Product
        fields = ('name', 'batch_data')

    def get_yearly_data(self, batches, interval,start_date):
        """
        Return yearly data.
        """
        current_year = start_date.year
        years = list(range(current_year-interval, current_year+1))
        data = []
        incoming_types = [
            txn_consts.ExternalTransactionType.INCOMING,
            txn_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE
        ]
        all_txn_types = incoming_types + [txn_consts.ExternalTransactionType.OUTGOING]
        ordered_txns = txn_models.ExternalTransaction.objects.filter(
            Q(result_batches__in=batches,type__in=all_txn_types,date__year__in=years,
              status=txn_consts.TransactionStatus.APPROVED)|Q(
            source_batches__in=batches,type__in=all_txn_types,date__year__in=years,
            status=txn_consts.TransactionStatus.APPROVED)
            ).distinct('date__year').order_by('date__year')
        if not ordered_txns:
            return data
        start_year = ordered_txns.first().date.year
        years = split_list(years,start_year,part2=True)
        for year in years:
            year_info = {}
            year_info['span'] = year
            year_info['receive'] = batches.filter(
                incoming_transactions__date__year=year,
                incoming_transactions__externaltransaction__type__in=all_txn_types,
                incoming_transactions__status=txn_consts.TransactionStatus.APPROVED
                ).aggregate(quantity=Sum('initial_quantity',default=0.0))['quantity']
            year_info['send'] = batches.filter(
                outgoing_transactions__date__year=year,
                outgoing_transactions__externaltransaction__type__in=all_txn_types,
                outgoing_transactions__status=txn_consts.TransactionStatus.APPROVED
                ).aggregate(quantity=Sum('outgoing_transaction_objects__quantity',default=0.00))['quantity']
            data.append(year_info)
        return data
    
    def get_monthly_data(self, batches, interval,start_date):
        """
        get monthly data.
        """
        dates = get_past_months(start_date, interval)
        dates.reverse()
        data = []
        incoming_types = [
            txn_consts.ExternalTransactionType.INCOMING,
            txn_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE
        ]
        all_txn_types = incoming_types + [txn_consts.ExternalTransactionType.OUTGOING]
        ordered_txns = txn_models.ExternalTransaction.objects.filter(
            Q(result_batches__in=batches,type__in=all_txn_types,date__gte=dates[0])|Q(
            source_batches__in=batches,type__in=all_txn_types,date__gte=dates[0])
            ).distinct('date').order_by('date')
        if not ordered_txns:
            return data
        txn_start_date = ordered_txns.first().date
        dates = split_list(dates,txn_start_date.replace(day=1),part2=True)
        for date in dates:
            month_info = {}
            month_info['span'] = date.strftime("%B %Y")
            month_info['receive'] = batches.filter(
                incoming_transactions__date__year=date.year,
                incoming_transactions__date__month=date.month,
                incoming_transactions__externaltransaction__type__in=all_txn_types,
                incoming_transactions__status=txn_consts.TransactionStatus.APPROVED
                ).aggregate(quantity=Sum('initial_quantity',default=0.0))['quantity']
            month_info['send'] = batches.filter(
                outgoing_transactions__date__year=date.year,
                outgoing_transactions__date__month=date.month,
                outgoing_transactions__externaltransaction__type__in=all_txn_types,
                outgoing_transactions__status=txn_consts.TransactionStatus.APPROVED
                ).aggregate(quantity=Sum('outgoing_transaction_objects__quantity',default=0.00))['quantity']
            data.append(month_info)
        return data
    
    def get_batch_data(self,product):
        """
        Return batch yearly batch send and receive data under the current node.
        """
        
        interval = int(self.context['request'].query_params.get(
            'interval', 12))
        duration = int(self.context['request'].query_params.get(
            'duration', dashboard_consts.Duration.YEARLY[0]))
        start_date = self.context['request'].query_params.get(
            'start_date', None)
        if start_date:
            start_date = read_date(start_date)
        if not start_date:
            start_date = timezone.now().date()
        batches = product.batches.filter(node=session.get_current_node())
        data = []
        if duration == dashboard_consts.Duration.YEARLY[0]:
            data = self.get_yearly_data(batches,interval,start_date)
        if duration == dashboard_consts.Duration.MONTHLY[0]:
            data = self.get_monthly_data(batches,interval,start_date)
        return data
    
    def to_representation(self, instance):
        """
        Overrided to update unit name in unit key.
        """
        data = super().to_representation(instance)
        data['unit'] = instance.unit.name
        return data


class ESGStatSerializer(serializers.Serializer):
    """
    Return risk statistics.
    """
    esg_stats = serializers.SerializerMethodField()

    supply_chain = None
    suppliers = node_models.Node.objects.none()

    class Meta:
        """
        Meta Info.
        """
        model = node_models.Node
        fields = ('esg_stats', )

    def __init__(self, *args, **kwargs):
        super(ESGStatSerializer, self).__init__(*args, **kwargs)
        try:
            sc_id = decode(self.context['request'].query_params.get(
                'supply_chain', None))
            self.supply_chain = supply_models.SupplyChain.objects.get(
                id=sc_id)
        except:
            pass
        self.suppliers = self.instance.get_connections(
                supply_chain=self.supply_chain).filter(is_supplier=True)
        
    def add_risk_score_to_suppliers(self,category=None):
        """
        Adds risk score suppliers based on the given category.
        """
        suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('overall')[:1]))
        if category == risk_consts.Category.ENVIRONMENT:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('environment')[:1]))
        elif category == risk_consts.Category.SOCIAL:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('social')[:1]))
        elif category == risk_consts.Category.GOVERNANCE:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('governance')[:1]))
        return suppliers

    def get_esg_stats(self,company):
        """
        Return stats related to esg scores.
        """
        category = int(self.context['request'].query_params.get(
            'risk_category', risk_consts.Category.OVERALL))
        suppliers = self.add_risk_score_to_suppliers(category=category)
        high_risk_suppliers = suppliers.filter(
            risk_score_value__lte=43).count()
        medium_risk_suplliers = suppliers.filter(
            risk_score_value__lte=60, risk_score_value__gt=43).count()
        low_risk_suppliers = suppliers.filter(risk_score_value__gt=60).count()
        total = self.suppliers.count()
        low_risk_info = {
            "suppliers": low_risk_suppliers,
            "percentage": percentage(low_risk_suppliers,total)
        }
        medium_risk_info = {
            "suppliers": medium_risk_suplliers,
            "percentage": percentage(medium_risk_suplliers,total)
        }
        high_risk_info = {
            "suppliers": high_risk_suppliers,
            "percentage": percentage(high_risk_suppliers,total)
        }
        esg_data = {
            "total_suppliers": total,
            "low_risk": low_risk_info, 
            "high_risk": high_risk_info,
            "medium_risk": medium_risk_info
        }
        return esg_data


class RiskStatSerializer(serializers.Serializer):
    """
    Return risk statistics.
    """
    sc_score_stats = serializers.SerializerMethodField()
    esg_score_stats = serializers.SerializerMethodField()

    supply_chain = None
    suppliers = node_models.Node.objects.none()

    class Meta:
        """
        Meta Info.
        """
        model = node_models.Node
        fields = ('esg_score_stats', 'sc_score_stats',)

    def __init__(self, *args, **kwargs):
        super(RiskStatSerializer, self).__init__(*args, **kwargs)
        try:
            sc_id = decode(self.context['request'].query_params.get(
                'supply_chain', None))
            self.supply_chain = supply_models.SupplyChain.objects.get(
                id=sc_id)
        except:
            pass
        self.suppliers = self.instance.get_connections(
                supply_chain=self.supply_chain).filter(is_supplier=True)
        
    def add_risk_score_to_suppliers(self,category=None):
        """
        Adds risk score suppliers based on the given category.
        """
        suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('overall')[:1]))
        if category == risk_consts.Category.ENVIRONMENT:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('environment')[:1]))
        elif category == risk_consts.Category.SOCIAL:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('social')[:1]))
        elif category == risk_consts.Category.GOVERNANCE:
            suppliers = self.suppliers.annotate(
            risk_score_value=Subquery(
            risk_models.RiskScore.objects.filter(
            node=OuterRef('pk')).order_by('-id').values('governance')[:1]))
        return suppliers
        
    def get_sc_score_stats(self,company):
        """
        Return sc score stats of the current node.
        includes esg of the current node and suppliers percentage.
        """
        node_sc = company.supply_chains.get(
            supply_chain=self.supply_chain)
        sc_data = {
            "risk_score": round(node_sc.sc_risk_score,2),
            "risk_level": node_sc.sc_risk_level
        }
        return sc_data
    
    def get_esg_score_stats(self,company):
        """
        ESG Score info.
        """
        environmental_low_suppliers = self.add_risk_score_to_suppliers(
            category=risk_consts.Category.ENVIRONMENT).filter(
            risk_score_value__gt=60).count()
        social_low_suppliers = self.add_risk_score_to_suppliers(
            category=risk_consts.Category.SOCIAL).filter(
            risk_score_value__gt=60).count()
        governance_low_suppliers = self.add_risk_score_to_suppliers(
            category=risk_consts.Category.GOVERNANCE).filter(
            risk_score_value__gt=60).count()
        total = self.suppliers.count()
        esg_data = {
            "environment": {
                "risk_score": round(company.risk_score.environment,2),
                "risk_level": company.risk_score.environment_risk_level,
                "low_risk_suppliers_percentage": percentage(
                    environmental_low_suppliers,total)
            }, 
            "social": {
                "risk_score": round(company.risk_score.social,2),
                "risk_level": company.risk_score.social_risk_level,
                "low_risk_suppliers_percentage": percentage(
                    social_low_suppliers,total)
            },
            "governance": {
                "risk_score": round(company.risk_score.governance,2),
                "risk_level": company.risk_score.governance_risk_level,
                "low_risk_suppliers_percentage": percentage(
                    governance_low_suppliers,total)
            }
        }
        return esg_data
