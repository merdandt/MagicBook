from concurrent.futures import ProcessPoolExecutor
import logging
import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI

from core.extractor import OptimizedEntityRelationshipExtractor
from core.prompts import relationships_prompts_map
from core.prompts import entity_prompt_map
from core.refference_mapping import reference_mapping_creator
from model.book_metadata import BookMetadata
from model.entity_types import EntityType, RelationshipType
from utils.file_utils import extract_text_from_pdf, clean_json_string
from utils.graph_utils import ensure_consistency
from core.graph_builder import create_graph_with_embeddings
from core.visualizer import create_plotly_graph

import streamlit as st


# Prompts for entity and relationship discovery
ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT = """
**Role**
You are a Literary Analysis Expert specializing in narrative structure, character development, and thematic elements.

**Task**
Analyze the provided book text to:
1. Extract all significant entities according to the predefined EntityType classification.
2. Identify relevant relationships between these entities based on the RelationshipType system.
3. Return a structured JSON object containing both entity lists and applicable relationship types.
"""

ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT = """
I need you to analyze a book and extract both its key entities and the relationships between them.
First, identify all significant entities in the book according to the EntityType enum.
Then, determine which relationship types from the RelationshipType enum apply to these entities.
Format your response as a JSON object with "Entities" and "Relationships" keys.

Here is the book text to analyze:
{book_text}

Remember to follow a careful chain of thought. First identify all entities, then determine their relationships.
"""

# Initialize LLM client
BOOK_LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",
    api_key=st.secrets["GEMINI_API_KEY"],
    temperature=0,
    max_output_tokens=None,
  )
async def extract_book_from_pdf(pdf_file, progress_callback=None):
    """
    Process a PDF file to extract book entities and relationships
    
    Args:
        pdf_file: Path to the PDF file
        progress_callback: Optional callback function to report progress
        
    Returns:
        tuple: (G_nx, entities, relationships, book_metadata)
    """
    start_time = time.time()
    
    # Extract text from PDF
    if progress_callback:
        progress_callback("Extracting text from PDF...")
    
    book_text = extract_text_from_pdf(pdf_file)
    if isinstance(book_text, str) and book_text.startswith("Error"):
        return None, None, None, None
    
    # Call LLM to discover entities and relationships
    if progress_callback:
        progress_callback("Analyzing text with AI...")
    
    try:
        # Format the messages for the LLM
        messages = [
            {"role": "system", "content": ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT.format(book_text=book_text[:10000])}
        ]
        
        # Call the LLM
        response = BOOK_LLM.invoke(messages)
        
        # Clean and parse the returned JSON
        cleaned_json = clean_json_string(response.content)
        book_entities_json = json.loads(cleaned_json)
        
        if progress_callback:
            progress_callback("Processing entity and relationship types...")
        
        # Ensure consistency in the entities and relationships
        ensured_entities, ensured_relationships = ensure_consistency(
            book_entities_json.get('Entities', []),
            book_entities_json.get('Relationships', []),
            {},  # Reference mappings would go here
            threshold=2
        )
        
        # Extract entities and relationships
        if progress_callback:
            progress_callback("Extracting entities and relationships...")
        
        # In a real implementation, this would call your entity extraction methods
        # For now, create placeholders
        entities_data = {entity_type: [] for entity_type in ensured_entities}
        relationships_data = {rel_type: [] for rel_type in ensured_relationships}
        
        # Create graph from extracted data
        if progress_callback:
            progress_callback("Building graph...")
        
        G_nx = create_graph_with_embeddings(entities_data, relationships_data)
        
        # Create book metadata
        end_time = time.time()
        processing_time = end_time - start_time
        
        book_name = "Extracted Book"  # Get a better name from PDF metadata if possible
        
        book_metadata = BookMetadata(
            book_name=book_name,
            author="Unknown",  # Extract from PDF metadata if possible
            pages_count=len(book_text.split('\n')),
            time_to_process=f"{processing_time:.2f} seconds",
            summary="Automatically extracted from PDF"
        )
        
        book_metadata.entities_map = entities_data
        book_metadata.relationships_map = relationships_data
        
        return G_nx, entities_data, relationships_data, book_metadata
        
    except Exception as e:
        logging.error(f"Error processing book: {e}")
        if progress_callback:
            progress_callback(f"Error: {e}")
        return None, None, None, None



async def create_graph_from_text(book_text, max_workers=5):
    """
    Create a graph from a book with optimized parallelization of LLM queries.
    
    Args:
        book_text: Text content of the book
        max_workers: Maximum number of concurrent workers for CPU-bound tasks
        
    Returns:
        Tuple of (graph, entities, relationships) or None if an error occurred
    """
    start = time.time()
    print('Starting graph creation...')
    
    # Create a ProcessPoolExecutor for CPU-bound tasks (text extraction, JSON parsing)
    process_executor = ProcessPoolExecutor(max_workers=max_workers)
    
    try:
        # Extract text from PDF (CPU-bound) using ProcessPoolExecutor
        loop = asyncio.get_running_loop()
        
        # Prepare messages for entity-relationship discovery
        messages = [
            {"role": "system", "content": ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT.format(book_text=book_text)}
        ]
        
        # Initial LLM query to discover entities and relationships
        # This is IO-bound so we use asyncio directly
        response = await asyncio.to_thread(BOOK_LLM.invoke, messages)
        
        print('LLM response received')
        # Process JSON in separate thread (CPU-bound)
        cleaned_json = await loop.run_in_executor(
            process_executor, 
            clean_json_string, 
            response.content
        )
        
        book_entities_json = await loop.run_in_executor(
            process_executor,
            json.loads,
            cleaned_json
        )
        
        reference_mappings = reference_mapping_creator()
        
        print('Processing entity and relationship types')
        # Ensure consistency in separate thread (CPU-bound)
        ensured_entities, ensured_relationships = await loop.run_in_executor(
            process_executor,
            ensure_consistency,
            book_entities_json['Entities'],
            book_entities_json['Relationships'],
            reference_mappings,
            2  # threshold
        )
        
        print('Ensured entities and relationships consistency')
        # Initialize optimized extractor
        extractor = OptimizedEntityRelationshipExtractor(
            chat_model=BOOK_LLM,
            entity_types=[EntityType[e] for e in ensured_entities],
            relationship_types=[RelationshipType[r] for r in ensured_relationships],
            entity_prompts_map=entity_prompt_map,
            relationship_prompts_map=relationships_prompts_map,
            reference_mappings=reference_mappings,
            book_text=book_text,
            max_workers=max_workers
        )
        
        print('Starting entity and relationship extraction')
        # Extract entities and relationships in parallel
        filled_entities, filled_relationships = await extractor.extract_all_async()
        
        print('Graph creation in progress...')
        # Create graph with embeddings (CPU-bound)
        G_nx = await loop.run_in_executor(
            process_executor,
            create_graph_with_embeddings,
            filled_entities, 
            filled_relationships
        )
        
        end = time.time()
        print(f"Time taken to process book: {end - start} seconds")
        return G_nx, extractor.book_metadata
        
    except Exception as e:
        logging.error(f"Error in create_graph_from_book: {e}", exc_info=True)
        return None
    finally:
        # Clean up resources
        process_executor.shutdown(wait=False)


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