def sync_node_risk_score(tenant=None):
    """
    Sync nodes risk score.
    """
    from v1.nodes.models import Node
    nodes = Node.objects.all()
    if tenant:
        nodes = nodes.filter(tenant=tenant)
    for node in nodes:
        try:
            node.initialize_risk_score()
        except:
            pass
