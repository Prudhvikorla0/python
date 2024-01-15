from neomodel import db


class CypherQuery:

    def __init__(self) -> None:
        pass

    def end_nodes(node_sc_id=None):
        """
        """
        query = """
                MATCH (n)
                WHERE NOT (n)-[:BUYS_FROM]->()
                RETURN n.pg_node_sc_id;
                """
        result = db.cypher_query(query)[0]
        response = [item for sublist in result for item in sublist]
        return response
    
    def connections(node_sc_id=None):
        """
        """
        query = """
                MATCH ({'pg_node_sc_id': {node_sc_id}})-[*]-(connected)
                RETURN connected.pg_node_sc_id;
                """%node_sc_id
        result = db.cypher_query(query)[0]
        response = [item for sublist in result for item in sublist]
        return response
    
    def parent_nodes(node_sc_id=None):
        """
        """
        query = """
                MATCH (endNode:NodeGraphModel {'pg_node_sc_id': {node_sc_id}}
                )<-[r:BUYS_FROM]-(startNode:NodeGraphModel)
                RETURN startNod.epg_node_sc_id;
                """%node_sc_id
        result = db.cypher_query(query)[0]
        response = [item for sublist in result for item in sublist]
        return response
    
    def child_nodes(node_sc_id=None):
        """
        """
        query = '''
        MATCH (startNode:NodeGraphModel {pg_node_sc_id:%s}
        )-[r:BUYS_FROM]->(endNode:NodeGraphModel)
        RETURN endNode.pg_node_sc_id;
        '''%node_sc_id
        result = db.cypher_query(query)[0]
        response = [item for sublist in result for item in sublist]
        return response

