from concurrent.futures import ProcessPoolExecutor
import logging
import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI

from core.extractor import EntityRelationshipExtractor

from core.prompts.relationships_prompts_map import RELATIONSHIP_PROMPTS_MAP
from core.prompts.entity_prompt_map import ENTITY_PROMPTS_MAP

from core.prompts.entity_discovery import ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT, ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT
from core.refference_mapping import reference_mapping_creator
from model.book_metadata import BookMetadata
from model.entity_types import EntityType, RelationshipType, enum_to_string
from utils.file_utils import extract_text_from_pdf, clean_json_string
from utils.graph_utils import ensure_consistency
from core.graph_builder import create_graph_with_embeddings
from core.visualizer import create_plotly_graph

import streamlit as st

# Initialize LLM client
BOOK_LLM = ChatGoogleGenerativeAI(
    # model="gemini-2.5-pro-exp-03-25",
    model="gemini-2.0-flash-lite",
    api_key=st.secrets["GEMINI_API_KEY"],
    temperature=0,
    max_output_tokens=None,
    
  )

def filter_valid_entity_types(entity_types, enum_class):
    """
    Filters a list of entity type strings to include only those that exist in the provided enum.
    
    Args:
        entity_types: List of entity type strings to filter
        enum_class: The enum class to check against (e.g., EntityType)
        
    Returns:
        List of valid entity type strings that exist in the enum
    """
    valid_types = []
    for entity_type in entity_types:
        try:
            # Check if the entity type exists in the enum
            enum_class[entity_type]
            valid_types.append(entity_type)
        except KeyError:
            # Log types that don't exist in the enum
            logging.warning(f"Entity type '{entity_type}' not found in {enum_class.__name__} enum, skipping")
    
    return valid_types


def filter_valid_relationship_types(relationship_types, enum_class):
    """
    Filters a list of relationship type strings to include only those that exist in the provided enum.
    
    Args:
        relationship_types: List of relationship type strings to filter
        enum_class: The enum class to check against (e.g., RelationshipType)
        
    Returns:
        List of valid relationship type strings that exist in the enum
    """
    valid_types = []
    for rel_type in relationship_types:
        try:
            # Check if the relationship type exists in the enum
            enum_class[rel_type]
            valid_types.append(rel_type)
        except KeyError:
            # Log types that don't exist in the enum
            logging.warning(f"Relationship type '{rel_type}' not found in {enum_class.__name__} enum, skipping")
    
    return valid_types



def create_graph_from_text(book_text, status_callback=None):
    """
    Create a graph from a book with synchronous processing.
    
    Args:
        book_text: Text content of the book
        
    Returns:
        Tuple of (graph, entities, relationships) or None if an error occurred
    """
    start = time.time()
    print('Starting graph creation...')

    if status_callback: status_callback("Extract entities and relationships...")
    try:
        # Prepare messages for entity-relationship discovery
        messages = [
            {"role": "system", "content": ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT.format(
                entity_type_enum=enum_to_string(EntityType),
                relationship_type_enum=enum_to_string(RelationshipType)
            )},
            {"role": "user", "content": ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT.format(book_text=book_text)}
        ]
        
        # Initial LLM query to discover entities and relationships
        response = BOOK_LLM.invoke(messages)
        cleaned_json = clean_json_string(response.content)
        print("Cleaned JSON:", cleaned_json)
        book_entities_json = json.loads(cleaned_json)
        reference_mappings = reference_mapping_creator()
        
        if status_callback: status_callback(f"Found {len(book_entities_json['Entities'])} entities and {len(book_entities_json['Relationships'])} relationships")

        ensured_entities, ensured_relationships = ensure_consistency(
            book_entities_json['Entities'],
            book_entities_json['Relationships'],
            reference_mappings,
            threshold=2
        )

        # Initialize extractor
        extractor = EntityRelationshipExtractor(
            chat_model=BOOK_LLM,
            entity_types=[EntityType[e] for e in ensured_entities],
            relationship_types=[RelationshipType[r] for r in ensured_relationships],
            entity_prompts_map=ENTITY_PROMPTS_MAP,
            relationship_prompts_map=RELATIONSHIP_PROMPTS_MAP,
            reference_mappings=reference_mappings,
            book_text=book_text,
            status_callback=status_callback
        )
        
        if status_callback: status_callback("Extracting entities and relationships...")
        # Extract entities and relationships
        filled_entities, filled_relationships = extractor.extract_all()
        
        if status_callback: status_callback("Creating graph with embeddings...")
        # Create graph with embeddings
        G_nx = create_graph_with_embeddings(
            filled_entities,
            filled_relationships
        )
        
        end = time.time()
        if status_callback: status_callback(f"Time taken to process book: {end - start} seconds")
        return G_nx, extractor.book_metadata
        
    except Exception as e:
        logging.error(f"Error in create_graph_from_book: {e}", exc_info=True)
        return None
        
        
def create_graph_from_book_metadata(book_metadata):
    """
    Create a NetworkX graph from book metadata
    
    Args:
        book_metadata: BookMetadata object
        
    Returns:
        networkx.MultiDiGraph: The graph
    """
    if not book_metadata or not book_metadata.entities_map or not book_metadata.relationships_map:
        logging.error("Cannot create graph: Invalid book metadata")
        return None
    
    try:
        return create_graph_with_embeddings(book_metadata.entities_map, book_metadata.relationships_map)
    except Exception as e:
        logging.error(f"Error creating graph: {e}")
        return None

def create_interactive_visualization(G, book_name):
    """
    Create an interactive visualization of the book graph
    
    Args:
        G: NetworkX graph
        book_name: Name of the book
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    if not G:
        return None
    
    try:
        return create_plotly_graph(G, book_name)
    except Exception as e:
        logging.error(f"Error creating visualization: {e}")
        return None

def analyze_book_entities(entities_data):
    """
    Generate a summary analysis of book entities
    
    Args:
        entities_data: Dictionary of entity lists
        
    Returns:
        dict: Analysis results
    """
    if not entities_data:
        return {}
    
    results = {}
    
    # Count entities by type
    entity_counts = {
        entity_type: len(entities) 
        for entity_type, entities in entities_data.items()
    }
    results['entity_counts'] = entity_counts
    
    # Get main characters (if CHARACTER type exists)
    if 'CHARACTER' in entities_data:
        main_characters = []
        for character in entities_data['CHARACTER']:
            if character.get('significance') == 'Main':
                main_characters.append({
                    'name': character.get('name', 'Unknown'),
                    'description': character.get('description', '')
                })
        results['main_characters'] = main_characters
    
    # Get main locations (if LOCATION type exists)
    if 'LOCATION' in entities_data:
        main_locations = []
        for location in entities_data['LOCATION']:
            if location.get('significance', '').lower() in ['main', 'important', 'key']:
                main_locations.append({
                    'name': location.get('name', 'Unknown'),
                    'description': location.get('description', '')
                })
        results['main_locations'] = main_locations
    
    # Get key events (if EVENT type exists)
    if 'EVENT' in entities_data:
        key_events = []
        for event in entities_data['EVENT']:
            key_events.append({
                'name': event.get('name', 'Unknown'),
                'summary': event.get('summary', '')
            })
        results['key_events'] = key_events[:5]  # Limit to top 5
    
    return results

def analyze_book_relationships(relationships_data):
    """
    Generate a summary analysis of book relationships
    
    Args:
        relationships_data: Dictionary of relationship lists
        
    Returns:
        dict: Analysis results
    """
    if not relationships_data:
        return {}
    
    results = {}
    
    # Count relationships by type
    relationship_counts = {
        rel_type: len(relationships) 
        for rel_type, relationships in relationships_data.items()
    }
    results['relationship_counts'] = relationship_counts
    
    # Get key relationship types
    key_relationship_types = sorted(
        relationship_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]  # Top 5
    
    results['key_relationship_types'] = [{
        'type': rel_type,
        'count': count
    } for rel_type, count in key_relationship_types]
    
    return results