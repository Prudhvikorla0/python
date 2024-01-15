"""
Functions to fetch data from the database and return as list of tuple pairs,
to be populated in the Excel template as dropdowns.

All function takes in 3 parameters as standard.

tenant          : Currently active tenant.
node            : Current node.
supply_chain    : Current supply chain.
"""

from v1.tenants import models as tenant_models
from v1.products import models as product_models

from v1.nodes import constants as node_constants


def get_countries(tenant, node, supply_chain, **kwargs):
    """
    Gets the selected countries for the tenant and return as list of tuple
    pairs of country name and encoded id
    """
    countries = tenant.countries.all() or tenant_models.Country.objects.all()
    return [(c.name, c.idencode) for c in countries]


def get_provinces(tenant, node, supply_chain, **kwargs):
    """
    Gets the provinces of selected countries for the tenant and
    return as list of tuple pairs of province name and encoded id
    """
    return [
        (p.name, p.idencode) for p in tenant_models.Province.objects.filter(
            country__tenants=tenant)
    ]


def get_producers(tenant, node, supply_chain, **kwargs):
    """
    Gets the list of producers directly connected to the node in the
    selected supply chain and returns as list of tuple pairs.
    """
    return [
        (f"{n.name}, {n.city}", n.idencode) for n in node.get_connections(
            supply_chain=supply_chain).filter(type=node_constants.NodeType.PRODUCER)
    ]


def get_products(tenant, node, supply_chain, **kwargs):
    """
    Gets the list of products in the supply chain.
    """
    return [(p.name, p.idencode) for p in supply_chain.products.all()]


def get_operations(tenant, node, supply_chain, **kwargs):
    """
    Gets the list of operations of the tenant.
    """
    return [
        (o.name, o.idencode) for o in tenant.node_operations.filter(
            node_type=node_constants.NodeType.PRODUCER
        )]


def get_currencies(tenant, node, supply_chain, **kwargs):
    """
    Gets the list of currencies enabled for the tenant.
    """
    return [(c.code, c.idencode) for c in tenant.currencies.all()]


def get_units(tenant, node, supply_chain, **kwargs):
    """
    Gets the list of units enabled for the tenant.
    """
    return [(u.name, u.idencode) for u in product_models.Unit.objects.all()]
