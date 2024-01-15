
from asgiref.local import Local

_active = Local()


def set_to_local(key, value):
    """ Sets attribute to Thread Local Storage"""
    setattr(_active, key, value)
    return True


def get_from_local(key, default=None):
    """ Gets attribute from Thread Local Storage"""
    return getattr(_active, key, default)


def get_current_user():
    """
    Returns the currently authenticated user when called while processing an API.
    Otherwise returns None.
    """
    from v1.accounts.models import CustomUser
    user = get_from_local('user', None)
    current_user = CustomUser.objects.filter(
        id=get_from_local('user_id')).first()
    if user and user == current_user:
        return user
    user = current_user
    set_to_local('user', user)
    return user


def get_current_node():
    """
    Returns the currently authenticated node when called while processing an API.
    Otherwise returns None.
    """
    from v1.nodes.models import Node
    node = get_from_local('node', None)
    current_node = Node.objects.filter(
        id=get_from_local('node_id')).first()
    if node and node == current_node:
        return node
    node = current_node
    set_to_local('node', node)
    return node


def get_current_tenant():
    """
    Returns the currently authenticated tenant when called while processing an API.
    Otherwise returns None.
    """
    from v1.tenants.models import Tenant
    tenant = get_from_local('tenant', None)
    current_tenant = Tenant.objects.filter(
        id=get_from_local('tenant_id')).first()
    if tenant and tenant == current_tenant:
        return tenant
    tenant = current_tenant
    set_to_local('tenant', tenant)
    return tenant

