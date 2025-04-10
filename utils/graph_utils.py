import logging
import networkx as nx

def extract_edge_ids(rel_type, relationship):
    """
    Extract source and target IDs from a relationship record based on its type.
    
    Args:
        rel_type: The relationship type string
        relationship: The relationship dictionary
        
    Returns:
        tuple: (source_id, target_id)
    """
    # Mapping relationship type to a lambda that returns (source_id, target_id)
    extractors = {
        # Family Relationships
        "Family_PARENT_OF": lambda r: (r.get("parent_id"), r.get("child_id")),
        "Family_SIBLING_OF": lambda r: (r.get("sibling1_id"), r.get("sibling2_id")),
        "Family_MARRIED_TO": lambda r: (r.get("spouse1_id"), r.get("spouse2_id")),
        
        # Emotional Relationships
        "Emotional_LOVES": lambda r: (r.get("lover_id"), r.get("beloved_id")),
        "Emotional_TRUSTS": lambda r: (r.get("trustor_id"), r.get("trusted_id")),
        "Emotional_BETRAYED": lambda r: (r.get("betrayer_id"), r.get("betrayed_id")),
        
        # Interaction Relationships
        "Interaction_INTERACTED_WITH": lambda r: (r.get("character1_id"), r.get("character2_id")),
        "Interaction_APPEARED_TOGETHER": lambda r: (r.get("character1_id"), r.get("character2_id")),
        "Interaction_MET_AT": lambda r: (r.get("character1_id"), r.get("character2_id")),
        
        # Location Relationships
        "Location_PRESENT_AT": lambda r: (r.get("character_id"), r.get("location_id")),
        "Location_TRAVELED_TO": lambda r: (r.get("character_id"), r.get("location_id")),
        "Location_BATTLE_AT": lambda r: (r.get("event_id"), r.get("location_id")),
        "Location_LIVES_IN": lambda r: (r.get("character_id"), r.get("location_id")),
        
        # Event Relationships
        "Event_WITNESSED": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_PARTICIPATED_IN": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_CAUSED": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_AFFECTED_BY": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_BORN_AT": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_DIED_AT": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_BEFORE": lambda r: (r.get("earlier_event_id"), r.get("later_event_id")),
        "Event_AFTER": lambda r: (r.get("later_event_id"), r.get("earlier_event_id")),
        "Event_SIMULTANEOUS_WITH": lambda r: (r.get("event1_id"), r.get("event2_id")),
        "Event_OVERLAPS_WITH": lambda r: (r.get("event1_id"), r.get("event2_id")),
        "Event_CAUSES": lambda r: (r.get("cause_event_id"), r.get("effect_event_id")),
        "Event_CAUSED_BY": lambda r: (r.get("effect_event_id"), r.get("cause_event_id")),
        
        # Organization Relationships
        "Organization_MEMBER_OF": lambda r: (r.get("character_id"), r.get("organization_id")),
        "Organization_LEADER_OF": lambda r: (r.get("character_id"), r.get("organization_id")),
        "Organization_FOUNDED_BY": lambda r: (r.get("organization_id"), r.get("founder_id")),
        
        # Creature Relationships
        "Creature_BELONGS_TO_SPECIES": lambda r: (r.get("character_id"), r.get("creature_id")),
        "Creature_CONTROLLED_BY": lambda r: (r.get("creature_id"), r.get("controller_id")),
        "Creature_ALLIED_WITH": lambda r: (r.get("creature_id"), r.get("ally_id")),
        
        # Conceptual Relationships
        "Concept_HAS_ABILITY": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_BELIEVES_IN": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_RESISTS": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_INFLUENCED_BY": lambda r: (r.get("character_id"), r.get("concept_id")),
        
        # Item Relationships
        "Item_POSSESSES": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_CREATED": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_SEEKS": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_DESTROYED": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_USED_IN": lambda r: (r.get("item_id"), r.get("event_id")),
        
        # Item-Item Relationships
        "ItemItem_COMPONENT_OF": lambda r: (r.get("component_id"), r.get("composite_item_id")),
        "ItemItem_COUNTERS": lambda r: (r.get("item1_id"), r.get("item2_id")),
        
        # Item-Location Relationships
        "ItemLocation_LOCATED_AT": lambda r: (r.get("item_id"), r.get("location_id")),
        "ItemLocation_ORIGINATED_FROM": lambda r: (r.get("item_id"), r.get("location_id")),
    }
    
    extractor = extractors.get(rel_type)
    if extractor:
        return extractor(relationship)
    
    # For unrecognized relationships, try to return the first two keys ending with "_id"
    id_keys = [k for k in relationship if k.endswith("_id")]
    if len(id_keys) >= 2:
        return relationship.get(id_keys[0]), relationship.get(id_keys[1])
    
    return None, None

def ensure_consistency(entities, relationships, reference_mappings, threshold=1):
    """
    Ensures consistency between entity types and relationship types using a single threshold.

    For each relationship, check its required entity types (via reference_mappings).
    - If a required entity type is missing and the number of relationships needing that entity is
      greater than or equal to the threshold, then add that entity type to the entity list.
    - Otherwise, remove relationships that require a missing entity.

    Parameters:
      entities: List[str]
          List of entity type strings (e.g., ["CHARACTER", "LOCATION", ...]).
      relationships: List[str]
          List of relationship type strings.
      reference_mappings: dict
          Dictionary mapping relationship names to a dict of required entity references.
          For example:
              {
                "Organization_MEMBER_OF": {
                    "Characters": ("CHARACTER", some_func),
                    "Organizations": ("ORGANIZATION", another_func)
                },
                ...
              }
      threshold: int
          The minimum number of relationships requiring a missing entity type to add it.
          Otherwise, any relationship that requires a missing entity (with count below threshold)
          will be removed.

    Returns:
      (updated_entities, updated_relationships): tuple
          The updated list of entity type strings and relationship type strings.
    """
    # Use a set for fast lookup.
    entities_set = set(entities)

    # First pass: Count missing occurrences for each entity type across all relationships.
    missing_counts = {}
    for rel in relationships:
        reqs = reference_mappings.get(rel, {})
        for key, (req_entity, _) in reqs.items():
            if req_entity not in entities_set:
                missing_counts[req_entity] = missing_counts.get(req_entity, 0) + 1

    # Second pass: Decide whether to keep or remove each relationship.
    updated_relationships = []
    for rel in relationships:
        reqs = reference_mappings.get(rel, {})
        missing_for_rel = []
        for key, (req_entity, _) in reqs.items():
            if req_entity not in entities_set:
                missing_for_rel.append(req_entity)
        # For each missing entity in this relationship, check if its count meets the threshold.
        # If any required entity does not meet the threshold, skip this relationship.
        remove_rel = False
        for missing_entity in missing_for_rel:
            if missing_counts.get(missing_entity, 0) < threshold:
                remove_rel = True
                break
        if remove_rel:
            continue
        # Otherwise, add any missing entity (that meets threshold) to the entities set.
        for missing_entity in missing_for_rel:
            entities_set.add(missing_entity)
        updated_relationships.append(rel)

    updated_entities = list(entities_set)
    return updated_entities, updated_relationships

def create_networkx_graph():
    """Create an empty NetworkX MultiDiGraph"""
    return nx.MultiDiGraph()

def add_node_to_graph(G, node_id, **attributes):
    """Add a node to the graph with given attributes"""
    G.add_node(node_id, **attributes)
    return G

def add_edge_to_graph(G, source_id, target_id, **attributes):
    """Add an edge to the graph with given attributes"""
    G.add_edge(source_id, target_id, **attributes)
    return G

def get_node_count(G):
    """Get the number of nodes in the graph"""
    return G.number_of_nodes()

def get_edge_count(G):
    """Get the number of edges in the graph"""
    return G.number_of_edges()

def get_node_types(G):
    """Get all unique node types in the graph"""
    types = set()
    for node, attrs in G.nodes(data=True):
        if 'entity_type' in attrs:
            types.add(attrs['entity_type'])
    return types

def get_edge_types(G):
    """Get all unique edge types in the graph"""
    types = set()
    for _, _, attrs in G.edges(data=True):
        if 'type' in attrs:
            types.add(attrs['type'])
    return types

def get_nodes_by_type(G, node_type):
    """Get all nodes of a specific type"""
    return [node for node, attrs in G.nodes(data=True) 
            if attrs.get('entity_type') == node_type]

def get_edges_by_type(G, edge_type):
    """Get all edges of a specific type"""
    return [(s, t) for s, t, attrs in G.edges(data=True) 
            if attrs.get('type') == edge_type]

def get_graph_stats(G):
    """Get basic statistics about the graph"""
    return {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'node_types': len(get_node_types(G)),
        'edge_types': len(get_edge_types(G)),
        'density': nx.density(G),
        'is_directed': nx.is_directed(G),
        'has_self_loops': any(nx.selfloop_edges(G)),
        'strongly_connected_components': len(list(nx.strongly_connected_components(G))) if nx.is_directed(G) else None,
        'weakly_connected_components': len(list(nx.weakly_connected_components(G))) if nx.is_directed(G) else None,
    }