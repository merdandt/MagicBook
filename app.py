import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import logging
import io
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define data structures
@dataclass
class BookMetadata:
    book_name: str
    author: str
    pages_count: int
    time_to_process: str
    summary: str
    entities_map: Optional[Dict[str, List[Dict[str, Any]]]] = None
    relationships_map: Optional[Dict[str, List[Dict[str, Any]]]] = None

# Global variables (using session_state)
if 'BOOK_METADATA_COLLECTION' not in st.session_state:
    st.session_state.BOOK_METADATA_COLLECTION = []
if 'CURRENT_BOOK_METADATA' not in st.session_state:
    st.session_state.CURRENT_BOOK_METADATA = None
if 'BOOK_NAME' not in st.session_state:
    st.session_state.BOOK_NAME = ""
if 'current_graph' not in st.session_state:
    st.session_state.current_graph = None
if 'current_entities' not in st.session_state:
    st.session_state.current_entities = {}
if 'current_relationships' not in st.session_state:
    st.session_state.current_relationships = {}

# Helper functions
def create_tree_display(entities, relationships):
    """Creates a hierarchical tree display of entities and relationships."""
    if not entities or not relationships:
        return "No entities or relationships to display"

    tree_text = []
    
    # ENTITIES TREE
    tree_text.append("ENTITIES")
    tree_text.append("========")
    
    entity_types = sorted(list(entities.keys()))
    
    for entity_type in entity_types:
        entities_of_type = entities[entity_type]
        count = len(entities_of_type)
        tree_text.append(f"├── {entity_type} ({count})")
        
        for i, entity in enumerate(entities_of_type):
            is_last = i == len(entities_of_type) - 1
            prefix = "└── " if is_last else "├── "
            name = entity.get("name", "Unnamed")
            key = entity.get("_key", "")
            tree_text.append(f"│   {prefix}{name} [{key}]")
    
    tree_text.append("")
    
    # RELATIONSHIPS TREE
    tree_text.append("RELATIONSHIPS")
    tree_text.append("=============")
    
    rel_types = sorted(list(relationships.keys()))
    
    for rel_type in rel_types:
        rels_of_type = relationships[rel_type]
        count = len(rels_of_type)
        tree_text.append(f"├── {rel_type} ({count})")
        
        for i, rel in enumerate(rels_of_type):
            is_last = i == len(rels_of_type) - 1
            prefix = "└── " if is_last else "├── "
            display_text = format_relationship(rel_type, rel)
            tree_text.append(f"│   {prefix}{display_text}")
    
    return "\n".join(tree_text)

def format_relationship(rel_type, rel):
    """Format a relationship based on its type and structure"""
    if "character_id" in rel and "event_id" in rel:
        return f"{rel['character_id']} → {rel['event_id']}"
    elif "character_id" in rel and "location_id" in rel:
        return f"{rel['character_id']} → {rel['location_id']}"
    elif "character_id" in rel and "item_id" in rel:
        return f"{rel['character_id']} → {rel['item_id']}"
    elif "character_id" in rel and "organization_id" in rel:
        return f"{rel['character_id']} → {rel['organization_id']}"
    elif "character1_id" in rel and "character2_id" in rel:
        return f"{rel['character1_id']} → {rel['character2_id']}"
    elif "spouse1_id" in rel:
        spouse2 = rel.get('spouse2_id', 'None')
        return f"{rel['spouse1_id']} → {spouse2}"
    elif "lover_id" in rel and "beloved_id" in rel:
        return f"{rel['lover_id']} → {rel['beloved_id']}"
    elif "earlier_event_id" in rel and "later_event_id" in rel:
        return f"{rel['earlier_event_id']} → {rel['later_event_id']}"
    else:
        keys = list(rel.keys())[:2]
        return f"{keys[0]}: {rel[keys[0]]}, {keys[1]}: {rel[keys[1]]}"

def load_cached_books():
    """Load metadata of all cached books"""
    if not st.session_state.BOOK_METADATA_COLLECTION:
        logging.warning("No cached books available")
        return []
    return st.session_state.BOOK_METADATA_COLLECTION

def select_cached_book(book_name):
    """Select a cached book by name from the collection"""
    books = load_cached_books()
    for book in books:
        if book.book_name == book_name:
            st.session_state.CURRENT_BOOK_METADATA = book
            return book
    logging.error(f"Book '{book_name}' not found in cached collection")
    return None

def get_cached_book_list():
    """Get list of cached book names for dropdown"""
    books = load_cached_books()
    return [book.book_name for book in books] if books else ["No cached books found"]

def create_graph_from_book(book_metadata_or_path):
    """Create a NetworkX graph from book metadata or PDF path"""
    # Create a simple demo graph
    G = nx.DiGraph()
    
    if isinstance(book_metadata_or_path, BookMetadata):
        book = book_metadata_or_path
        
        if book.entities_map:
            for entity_type, entities in book.entities_map.items():
                for entity in entities:
                    G.add_node(entity.get('_key', f"unknown-{time.time()}"), 
                              type=entity_type, 
                              name=entity.get('name', 'Unnamed'))
        
        if book.relationships_map:
            for rel_type, relationships in book.relationships_map.items():
                for rel in relationships:
                    if "character_id" in rel and "event_id" in rel:
                        G.add_edge(rel["character_id"], rel["event_id"], type=rel_type)
                    elif "character1_id" in rel and "character2_id" in rel:
                        G.add_edge(rel["character1_id"], rel["character2_id"], type=rel_type)
    else:
        # Demo graph for PDF upload
        G.add_node("character1", type="character", name="Character 1")
        G.add_node("character2", type="character", name="Character 2")
        G.add_node("location1", type="location", name="Location 1")
        G.add_edge("character1", "character2", type="knows")
        G.add_edge("character1", "location1", type="visits")
        
        # Sample data
        entities = {
            "character": [
                {"_key": "character1", "name": "Character 1"},
                {"_key": "character2", "name": "Character 2"}
            ],
            "location": [
                {"_key": "location1", "name": "Location 1"}
            ]
        }
        
        relationships = {
            "knows": [
                {"character1_id": "character1", "character2_id": "character2"}
            ],
            "visits": [
                {"character_id": "character1", "location_id": "location1"}
            ]
        }
        
        st.session_state.current_entities = entities
        st.session_state.current_relationships = relationships
    
    return G

def visualize_graph_network(G, title="Book Graph"):
    """Create a matplotlib visualization of the graph"""
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    
    node_types = nx.get_node_attributes(G, 'type')
    
    unique_types = set(node_types.values())
    color_map = {}
    colors = plt.cm.tab10.colors
    for i, type_name in enumerate(unique_types):
        color_map[type_name] = colors[i % len(colors)]
    
    for node_type in unique_types:
        nodelist = [node for node, data in G.nodes(data=True) if data.get('type') == node_type]
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=nodelist,
                              node_color=color_map[node_type],
                              node_size=500,
                              alpha=0.8,
                              label=node_type)
    
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    
    node_labels = {node: data.get('name', node) for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    
    plt.title(title)
    plt.legend()
    plt.axis("off")
    
    return plt.gcf()

def creare_adb_graph(G, book_name):
    """Placeholder for creating an Arango database graph"""
    logging.info(f"Creating ArangoDB graph for book: {book_name}")
    return True

def handle_cached_book_selection(book_name):
    """Handle cached book selection from dropdown"""
    if book_name == "No cached books found":
        st.error("No cached books available")
        return None
    
    book = select_cached_book(book_name)
    if not book:
        st.error(f"Error: Could not find book '{book_name}'")
        return None
    
    G_nx = create_graph_from_book(book)
    if not G_nx:
        st.error(f"Error: Could not create graph for book '{book_name}'")
        return None
    
    st.session_state.current_graph = G_nx
    st.session_state.current_entities = book.entities_map
    st.session_state.current_relationships = book.relationships_map
    st.session_state.BOOK_NAME = book.book_name
    
    info_text = (
        f"Book: {book.book_name}\n"
        f"Author: {book.author}\n"
        f"Pages: {book.pages_count}\n"
        f"Processing time: {book.time_to_process}\n\n"
        f"Entities: {len(book.entities_map) if book.entities_map else 0} types\n"
        f"Relationships: {len(book.relationships_map) if book.relationships_map else 0} types\n\n"
        f"Summary: {book.summary}"
    )
    
    return info_text

def handle_pdf_upload(pdf_file):
    """Handle PDF upload and processing"""
    if pdf_file is None:
        st.error("No PDF file provided")
        return None
    
    pdf_bytes = pdf_file.read()
    
    # Demo graph for now
    G_nx = create_graph_from_book(pdf_bytes)
    
    if not G_nx:
        st.error("Error processing PDF")
        return None
    
    st.session_state.current_graph = G_nx
    st.session_state.BOOK_NAME = pdf_file.name.replace('.pdf', '')
    
    entity_count = sum(len(ent_list) for ent_list in st.session_state.current_entities.values()) if st.session_state.current_entities else 0
    rel_count = sum(len(rel_list) for rel_list in st.session_state.current_relationships.values()) if st.session_state.current_relationships else 0
    
    info_text = (
        f"Book: {st.session_state.BOOK_NAME}\n"
        f"Entities extracted: {entity_count}\n"
        f"Relationships extracted: {rel_count}\n"
        f"Graph created with {len(G_nx.nodes)} nodes and {len(G_nx.edges)} edges"
    )
    
    return info_text

def save_processed_book(book_name):
    """Save processed book to cache"""
    if not st.session_state.current_graph:
        return "No graph to save"
    
    try:
        creare_adb_graph(st.session_state.current_graph, book_name)
        
        book_metadata = BookMetadata(
            book_name=book_name,
            author="Extracted from PDF",
            pages_count=len(st.session_state.current_graph.nodes),
            time_to_process=f"{time.time()} seconds",
            summary="Automatically extracted from PDF"
        )
        book_metadata.entities_map = st.session_state.current_entities
        book_metadata.relationships_map = st.session_state.current_relationships
        
        st.session_state.BOOK_METADATA_COLLECTION.append(book_metadata)
        
        return f"Book '{book_name}' saved successfully with {len(st.session_state.current_graph.nodes)} nodes and {len(st.session_state.current_graph.edges)} edges"
    except Exception as e:
        logging.error(f"Error saving book: {e}")
        return f"Error saving book: {str(e)}"

def chat_response(message, history):
    """Chat response function"""
    if not history:
        history = []
    history.append({"user": message, "bot": f"You asked about: {message}"})
    return history

# Define the Streamlit app
def main():
    st.set_page_config(
        page_title="MagicBook: Book Graph Explorer",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize app state if not set
    if 'app_state' not in st.session_state:
        st.session_state.app_state = "choose_book"
    
    # Navigation function to switch between states
    def navigate_to(state):
        st.session_state.app_state = state
    
    # CHOOSE BOOK STATE
    if st.session_state.app_state == "choose_book":
        st.title("MagicBook: Dynamic Book Relationship Visualization")
        st.write("Select a cached book or upload a new PDF to analyze.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cached Books")
            cached_books = get_cached_book_list()
            cached_book_selection = st.selectbox(
                "Select a cached book",
                cached_books
            )
            
            load_cached = st.button("Load Cached Book")
            
            if load_cached:
                with st.spinner("Loading book..."):
                    info_text = handle_cached_book_selection(cached_book_selection)
                    if info_text:
                        st.session_state.info_text = info_text
                        navigate_to("interaction")
        
        with col2:
            st.subheader("Upload New Book")
            pdf_file = st.file_uploader("Upload PDF Book", type=["pdf"])
            
            process_pdf = st.button("Process PDF")
            
            if process_pdf and pdf_file is not None:
                with st.spinner("Processing PDF..."):
                    # Simulate processing delay
                    time.sleep(2)
                    info_text = handle_pdf_upload(pdf_file)
                    if info_text:
                        st.session_state.info_text = info_text
                        navigate_to("interaction")
    
    # INTERACTION STATE
    elif st.session_state.app_state == "interaction":
        st.title("Book Interaction Interface")
        
        # Back button at the top
        if st.button("← Back to Book Selection"):
            navigate_to("choose_book")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Show book info
            st.text_area(
                "Book Information",
                value=st.session_state.info_text,
                height=200,
                disabled=True
            )
            
            # Show entities and relationships
            if st.session_state.current_entities and st.session_state.current_relationships:
                tree_display = create_tree_display(
                    st.session_state.current_entities,
                    st.session_state.current_relationships
                )
                st.text_area(
                    "Entities & Relationships",
                    value=tree_display,
                    height=400,
                    disabled=True
                )
            
            # Save book functionality
            with st.expander("Save Book"):
                book_name = st.text_input("Book Name", value=st.session_state.BOOK_NAME)
                
                if st.button("Save Book to Cache"):
                    with st.spinner("Saving book..."):
                        save_status = save_processed_book(book_name)
                        st.success(save_status)
        
        with col2:
            # Graph visualization
            if st.session_state.current_graph:
                st.subheader("Book Graph Visualization")
                fig = visualize_graph_network(st.session_state.current_graph, st.session_state.BOOK_NAME)
                st.pyplot(fig)
            
            # Chat interface
            st.subheader("Ask about the book")
            
            # Initialize chat history if not exists
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(message["user"])
                with st.chat_message("assistant"):
                    st.write(message["bot"])
            
            # Chat input
            user_input = st.chat_input("Ask a question about the book")
            
            if user_input:
                with st.chat_message("user"):
                    st.write(user_input)
                
                with st.spinner("Thinking..."):
                    # Process the user's question
                    st.session_state.chat_history = chat_response(
                        user_input, 
                        st.session_state.chat_history
                    )
                
                with st.chat_message("assistant"):
                    st.write(st.session_state.chat_history[-1]["bot"])