import networkx as nx

from embedding.embedding_model import generate_embedding
from embedding.id_extractor import extract_edge_ids


# Example of updating entities and creating a NetworkX graph with embeddings
def create_graph_with_embeddings(entities_data, relationships_data):
    G = nx.MultiDiGraph()

    # Generate embeddings and add nodes
    for entity_type, entities in entities_data.items():
        for entity in entities:
            node_id = entity['_key']
            node_attrs = entity.copy()
            node_attrs['entity_type'] = entity_type

            text = entity.get('summary') or entity.get('description')
            if text:
                node_attrs['embedding'] = generate_embedding(text)

            G.add_node(node_id, **node_attrs)

    # Add edges
    for rel_type, relationships in relationships_data.items():
        for relationship in relationships:
            source_id, target_id = extract_edge_ids(rel_type, relationship)
            if source_id and target_id and G.has_node(source_id) and G.has_node(target_id):
                G.add_edge(source_id, target_id, type=rel_type, **relationship)

    return G