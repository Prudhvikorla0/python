
from django.db import models
from django.utils import timezone

from base import session

from v1.supply_chains.models import NodeSupplyChain, SupplyChain
from v1.supply_chains.constants import ConnectionInitiation

from v1.tenants.models import Tenant
from v1.nodes.models import Node

from v1.supply_chains import graph_queries

from v1.risk import models as risk_models

from v1.nodes import constants as node_consts


class UpdateScore:
    """
    Class To Update Supply Chain Risk Score.
    """
    def __init__(self) -> None:
        self.updated_node_scs = []

    def calculate_score(self,node_sc,looped_node_scs=[]):
        """
        Function for calculation sc risk score.
        """
        node = node_sc.node
        sc = node_sc.supply_chain
        connections = node.get_connections(
            supply_chain=sc.id,supplied=True)
        risk_score = node.get_risk_score()
        sc_risk_score = 0
        if not connections:
            looped_node_scs.append(node_sc.id)
            if node.type == node_consts.NodeType.PRODUCER:
                sc_risk_score = 100
        else:
            looped_node_scs.append(node_sc.id)
            connection_node_scs = NodeSupplyChain.objects.filter(
                node__in=connections,supply_chain=sc)
            for connetion_node_sc in connection_node_scs:
                if connetion_node_sc.id in self.updated_node_scs:
                    sc_risk_score += connetion_node_sc.sc_risk_score
                elif connetion_node_sc.id in looped_node_scs:
                    sc_risk_score += connetion_node_sc.node.get_risk_score()
                else:
                    score = self.calculate_score(
                        connetion_node_sc,looped_node_scs)
                    sc_risk_score += score
            try:
                sc_risk_score = sc_risk_score/connection_node_scs.count()
            except:
                pass
        node_sc.sc_risk_score = (sc_risk_score+risk_score)/2
        node_sc.sc_risk_updated_on = timezone.now()
        node_sc.save()
        self.updated_node_scs.append(node_sc.id)
        return node_sc.sc_risk_score
    
    def update_sc_score(self,tenant):
        """
        Function updates sc risk score of all node supplychains.
        """
        self.updated_node_scs = []
        node_scs = NodeSupplyChain.objects.filter(
            node__tenant=tenant).order_by('id')
        for node_sc in node_scs:
            if node_sc.id not in self.updated_node_scs:
                self.calculate_score(node_sc,[])


class GraphUpdateScore:

    def __init__(self):
        self.score_updated_nodes = []

    def check_score(self,node_sc):
        target_connections = graph_queries.CypherQuery.child_nodes(node_sc_id=node_sc.id)
        new_node_scs = NodeSupplyChain.objects.filter(id__in=target_connections)
        if target_connections and set(target_connections).issubset(set(self.score_updated_nodes)):
            node_sc.sc_risk_score = (new_node_scs.aggregate(
                total=models.Sum('sc_risk_score'))['total']+node_sc.node.risk_score.overall)/(
                new_node_scs.count() + 1)
            node_sc.sc_risk_updated_on = timezone.now
            node_sc.save()
            self.score_updated_nodes.append(node_sc.id)
        if not target_connections:
            self.calculate_risk()
        for new_node_sc in new_node_scs:
            self.check_score(new_node_sc)

    
    def calculate_risk(self, tenant=None):
        scs = SupplyChain.objects.filter(tenant=tenant)
        for sc in scs:
            node_scs = sc.node_supplychains.all().exclude(id__in=self.score_updated_nodes)
            if not node_scs:
                continue
            for node_sc in node_scs:
                node = node_sc.node
                if node.risk_score:
                    node_sc.sc_risk_score = node.risk_score.overall
                    node_sc.sc_risk_updated_on = timezone.now
                    node_sc.save()
                    self.score_updated_nodes.append(node_sc.id)
                self.check_score(node_sc)


# class UpdateScore:

#     def __init__(self):
#         self.score_updated_nodes = []
#         self.looped_nodes = []
#         self.avoid_nodes = []

#     def end_node_score_calculation(self,node_sc,connections):
#         """
#         """
#         node = node_sc.node
#         sc = node_sc.supply_chain
#         system_connections = node.get_connections(
#             supply_chain=sc,suppliers=True).exclude(id__in=connections)
#         risk_score = node.risk_score.overall
#         if node.type == node_consts.NodeType.PRODUCER:
#             risk_score = 100
#         if system_connections:
#             system_connection_score = sum(system_connections.annotate(
#                 risk_score_value=models.Subquery(
#                 risk_models.RiskScore.objects.filter(
#                 node=models.OuterRef('pk')).order_by(
#                 '-id').values('overall')[:1])).values_list(
#                 'risk_score_value',flat=True))
#             current_sc_avg = system_connection_score/system_connections.count()
#             risk_score = (risk_score+current_sc_avg)/2
#         node_sc.sc_risk_score = risk_score
#         node_sc.sc_risk_updated_on = timezone.now()
#         node_sc.save()

#     def inner_node_score_calculation(self,node_sc,connections,connection_scs):
#         """
#         """
#         node = node_sc.node
#         sc = node_sc.supply_chain
#         system_connections = node.get_connections(
#                 supply_chain=sc,suppliers=True).exclude(id__in=connections)
#         system_connection_score = sum(system_connections.annotate(
#             risk_score_value=models.Subquery(
#             risk_models.RiskScore.objects.filter(
#             node=models.OuterRef('pk')).order_by(
#             '-id').values('overall')[:1])).values_list('risk_score_value',flat=True))
#         total_sc_connection_score = (
#             connection_scs.aggregate(total=models.Sum('sc_risk_score'))['total']+system_connection_score)
#         total_sc_connections = connection_scs.count()+system_connections.count()
#         avoide_nodes = node.get_connections(
#             supply_chain=sc,manual=True,suppliers=True).filter(
#             id__in=self.avoid_nodes)
#         avoide_scores = sum(avoide_nodes.annotate(
#             risk_score_value=models.Subquery(
#             risk_models.RiskScore.objects.filter(
#             node=models.OuterRef('pk')).order_by(
#             '-id').values('overall')[:1])).values_list('risk_score_value',flat=True))
#         current_sc_avg = (total_sc_connection_score+avoide_scores)/(
#             total_sc_connections+avoide_nodes.count())
#         node_sc.sc_risk_score = (current_sc_avg+node_sc.node.risk_score.overall)/2
#         node_sc.sc_risk_updated_on = timezone.now()
#         node_sc.save()

#     def get_node_scs(self,connections,sc):
#         """
#         """
#         new_node_scs = NodeSupplyChain.objects.filter(
#             node__in=connections, supply_chain=sc).exclude(
#             id__in=self.score_updated_nodes).exclude(id__in=self.score_updated_nodes)
#         for new_node_sc in new_node_scs:
#             self.check_score(new_node_sc)

#     def check_score(self,node_sc):
#         node = node_sc.node
#         sc = node_sc.supply_chain
#         connections = node.get_connections(
#             supply_chain=sc,manual=True,suppliers=True)
#         if not connections:
#             if node.risk_score:
#                 self.end_node_score_calculation(node_sc,connections)
#             self.score_updated_nodes.append(node_sc.id)
#             self.looped_nodes = []
#             target_connections = Node.objects.filter(
#                 source_connections__target=node, supply_chains__supply_chain=sc, 
#                 source_connections__initiation=ConnectionInitiation.MANUAL,
#                 source_connections__is_supplier=True,
#                 )
#             if not target_connections:
#                 self.calculate_risk()
#             self.get_node_scs(target_connections,sc)
#         current_scs = NodeSupplyChain.objects.filter(
#                 node__in=connections, supply_chain=sc).exclude(
#                 id__in=self.avoid_nodes)
#         if current_scs and set(current_scs.values_list('id',flat=True)).issubset(set(self.score_updated_nodes)):
#             self.inner_node_score_calculation(node_sc,connections,current_scs)
#             self.score_updated_nodes.append(node_sc.id)
#             target_connections = Node.objects.filter(
#                 source_connections__target=node, supply_chains__supply_chain=sc, 
#                 source_connections__initiation=ConnectionInitiation.MANUAL,
#                 source_connections__is_supplier=True,)
#             self.looped_nodes = []
#             if not target_connections:
#                 self.calculate_risk(tenant=node.tenant)
#             self.get_node_scs(target_connections,sc)
#         else:
#             if node_sc.id in self.looped_nodes:
#                 self.avoid_nodes.append(node_sc.id)
#             self.looped_nodes.append(node_sc.id)
#             self.get_node_scs(connections,sc)
    
#     def calculate_risk(self,tenant=None):
#         scs = SupplyChain.objects.filter(tenant=tenant)
#         for sc in scs:
#             node_scs = sc.node_supplychains.all().exclude(
#                 id__in=self.score_updated_nodes)
#             if not node_scs:
#                 continue
#             for node_sc in node_scs:
#                 self.check_score(node_sc)
