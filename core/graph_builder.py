import logging
import networkx as nx
from typing import Dict, List, Optional

from utils.embedding import generate_embedding
from utils.graph_utils import extract_edge_ids

def create_graph_with_embeddings(entities_data, relationships_data):
    """
    Create a NetworkX graph with embeddings from entities and relationships data.
    
    Args:
        entities_data: Dictionary of entity lists
        relationships_data: Dictionary of relationship lists
        
    Returns:
        nx.MultiDiGraph: The constructed graph
    """
    G = nx.MultiDiGraph()
    
    # Generate embeddings and add nodes
    for entity_type, entities in entities_data.items():
        for entity in entities:
            node_id = entity.get('_key')
            if not node_id:
                logging.warning(f"Skipping entity without _key: {entity}")
                continue
                
            # Create node attributes
            node_attrs = entity.copy()
            node_attrs['entity_type'] = entity_type
            
            # Generate embedding if text exists
            text = entity.get('summary') or entity.get('description')
            if text:
                node_attrs['embedding'] = generate_embedding(text)
            
            # Add node to graph
            G.add_node(node_id, **node_attrs)
    
    # Add edges
    for rel_type, relationships in relationships_data.items():
        for relationship in relationships:
            source_id, target_id = extract_edge_ids(rel_type, relationship)
            
            if source_id and target_id and G.has_node(source_id) and G.has_node(target_id):
                # Create edge attributes
                edge_attrs = relationship.copy()
                edge_attrs['type'] = rel_type
                
                # Add edge to graph
                G.add_edge(source_id, target_id, **edge_attrs)
            else:
                logging.debug(f"Skipping edge {source_id} -> {target_id} for {rel_type}: missing nodes")
    
    logging.info(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G

def get_character_basic(c):
    """Extract basic character properties"""
    return {"_key": c["_key"], "name": c["name"]}

def get_character_standard(c):
    """Extract standard character properties"""
    return {**get_character_basic(c), "significance": c.get("significance", "")}

def get_character_detailed(c):
    """Extract detailed character properties"""
    return {**get_character_standard(c), "gender": c.get("gender", ""), "description": c.get("description", "")}

def get_location_basic(l):
    """Extract basic location properties"""
    return {"_key": l["_key"], "name": l["name"]}

def get_location_typed(l):
    """Extract typed location properties"""
    return {**get_location_basic(l), "type": l.get("type", "")}

def get_event_basic(e):
    """Extract basic event properties"""
    return {"_key": e["_key"], "name": e["name"]}

def get_event_detailed(e):
    """Extract detailed event properties"""
    return {**get_event_basic(e), "type": e.get("type", ""), "summary": e.get("summary", "")}

def add_entity_subgraph(G, entity_id, depth=1):
    """
    Add a subgraph of connected entities to a new graph.
    
    Args:
        G: Source graph
        entity_id: ID of the central entity
        depth: How many hops from the central entity to include
        
    Returns:
        nx.MultiDiGraph: Subgraph
    """
    if entity_id not in G:
        logging.warning(f"Entity {entity_id} not found in graph")
        return nx.MultiDiGraph()
    
    # Create empty graph
    subgraph = nx.MultiDiGraph()
    
    # Add central entity
    central_attrs = G.nodes[entity_id]
    subgraph.add_node(entity_id, **central_attrs)
    
    # Set of nodes to process and nodes already processed
    to_process = {entity_id}
    processed = set()
    current_depth = 0
    
    while current_depth < depth and to_process:
        next_to_process = set()
        
        for node in to_process:
            processed.add(node)
            
            # Get outgoing edges
            for _, target, edge_data in G.out_edges(node, data=True):
                # Add edge
                subgraph.add_edge(node, target, **edge_data)
                # Add target node with its attributes
                if target not in subgraph:
                    target_attrs = G.nodes[target]
                    subgraph.add_node(target, **target_attrs)
                # Add to next round if not already processed
                if target not in processed:
                    next_to_process.add(target)
                    
            # Get incoming edges
            for source, _, edge_data in G.in_edges(node, data=True):
                # Add edge
                subgraph.add_edge(source, node, **edge_data)
                # Add source node with its attributes
                if source not in subgraph:
                    source_attrs = G.nodes[source]
                    subgraph.add_node(source, **source_attrs)
                # Add to next round if not already processed
                if source not in processed:
                    next_to_process.add(source)
        
        # Update for next iteration
        to_process = next_to_process
        current_depth += 1
    
    return subgraph

def get_largest_connected_component(G):
    """Get the largest connected component in the graph."""
    if not G:
        return nx.MultiDiGraph()
        
    if nx.is_directed(G):
        components = list(nx.weakly_connected_components(G))
    else:
        components = list(nx.connected_components(G))
    
    if not components:
        return G  # Return original graph if no components found
    
    # Get the largest component
    largest_component = max(components, key=len)
    return G.subgraph(largest_component).copy()

def filter_graph_by_entity_types(G, entity_types):
    """
    Filter graph to only include nodes of specified entity types.
    
    Args:
        G: Input graph
        entity_types: List of entity type strings to keep
        
    Returns:
        nx.MultiDiGraph: Filtered graph
    """
    if not entity_types:
        return G
        
    nodes_to_keep = [
        node for node, attrs in G.nodes(data=True)
        if attrs.get('entity_type') in entity_types
    ]
    
    return G.subgraph(nodes_to_keep).copy()

def filter_graph_by_relationship_types(G, relationship_types):
    """
    Filter graph to only include edges of specified relationship types.
    
    Args:
        G: Input graph
        relationship_types: List of relationship type strings to keep
        
    Returns:
        nx.MultiDiGraph: Filtered graph
    """
    if not relationship_types:
        return G
    
    filtered_G = nx.MultiDiGraph()
    
    # Copy all nodes
    for node, attrs in G.nodes(data=True):
        filtered_G.add_node(node, **attrs)
    
    # Copy only edges with matching relationship types
    for source, target, key, attrs in G.edges(data=True, keys=True):
        if attrs.get('type') in relationship_types:
            filtered_G.add_edge(source, target, key=key, **attrs)
    
    return filtered_G