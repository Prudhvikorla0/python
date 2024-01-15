"""
Graph models for the supply chain
These models are not connected to the RDBMS, Postgres, but to the Neo4j database.
A skeletal approach is used to minimize the data redundancy across multiple
databases. Only very minimal information required for querying is added to the graph.
Any further information required is then fetched from the RDBMS database.
The ideology behind the implementation is to speed up recursive queries in fetching
the connections of an actor
"""

import neomodel
from neomodel import cardinality

from django.utils.timezone import datetime


class BaseStructuredNode(neomodel.StructuredNode):
    uid = neomodel.UniqueIdProperty()
    created_on = neomodel.DateTimeProperty(default=datetime.now)
    updated_on = neomodel.DateTimeProperty(default=datetime.now)

    __abstract_node__ = True

    def save(self):
        self.updated_on = datetime.now()
        super(BaseStructuredNode, self).save()


class ConnectionRel(neomodel.StructuredRel):
    created_on = neomodel.DateTimeProperty(default=datetime.now)
    supply_chain_id = neomodel.IntegerProperty()
    status = neomodel.IntegerProperty()
    active = neomodel.BooleanProperty(default=True)
    tags = neomodel.JSONProperty()


class NodeGraphModel(BaseStructuredNode):
    """
    Graph node model to store minimal information about the node.
    """
    pg_node_id = neomodel.IntegerProperty()
    pg_node_idencode = neomodel.StringProperty(required=True)
    pg_node_sc_id = neomodel.IntegerProperty()
    pg_node_sc_idencode = neomodel.StringProperty(required=True)

    type = neomodel.IntegerProperty(required=True)
    full_name = neomodel.StringProperty(required=True)
    managers = neomodel.JSONProperty()

    suppliers = neomodel.RelationshipTo('NodeGraphModel', 'BUYS_FROM', model=ConnectionRel)
    buyers = neomodel.RelationshipFrom('NodeGraphModel', 'SUPPLY_TO', model=ConnectionRel)

    def disconnect_all(self):
        self.suppliers.disconnect_all()
        self.buyers.disconnect_all()
        return True
