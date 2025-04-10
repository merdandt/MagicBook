import streamlit as st
import networkx as nx
import pandas as pd
import time
import asyncio
import os
import logging
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import local modules
from utils.file_utils import extract_text_from_pdf
from utils.embedding import load_embedding_model
from model.book_metadata import BookMetadata
from services.cache_service import (load_cached_books, get_cached_book_list, 
                                   select_cached_book, save_book_metadata,
                                   delete_cached_book)
from services.graph_service import (create_graph_from_book_metadata, create_graph_from_text, 
                                   create_interactive_visualization,
                                   analyze_book_entities, analyze_book_relationships)
from services.db_service import is_db_connected, create_arango_graph
from core.visualizer import create_tree_display

import asyncio
import threading
import warnings

# Filter out the torch.classes warning
warnings.filterwarnings("ignore", message="Examining the path of torch.classes")

# Set page configuration
st.set_page_config(
    page_title="MagicBook: Dynamic Book Relationship Visualization",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark mode support
st.markdown("""
<style>
    /* Base styles that work for both light and dark mode */
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Message boxes with dark mode support */
    .success-message {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .error-message {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .info-message {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* Light mode styles */
    @media (prefers-color-scheme: light) {
        .main-header {
            color: #1E3D59;
        }
        .sub-header {
            color: #1E3D59;
        }
        .success-message {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        .error-message {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        .info-message {
            color: #0c5460;
            background-color: #d1ecf1;
            border-color: #bee5eb;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F5F5F5;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4c78a8;
            color: white;
        }
    }
    
    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #7FDBFF;
        }
        .sub-header {
            color: #7FDBFF;
        }
        .success-message {
            color: #d4edda;
            background-color: #155724;
            border-color: #0f4c19;
        }
        .error-message {
            color: #f8d7da;
            background-color: #721c24;
            border-color: #5c171d;
        }
        .info-message {
            color: #d1ecf1;
            background-color: #0c5460;
            border-color: #0a444d;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #2E2E2E;
            color: #E1E1E1;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5;
            color: #FFFFFF;
        }
        
        /* Additional dark mode adjustments for Streamlit elements */
        .stDataFrame {
            border: 1px solid #444;
        }
        .stMarkdown code {
            background-color: #2E2E2E !important;
            color: #E1E1E1 !important;
        }
        .stButton>button {
            border: 1px solid #555 !important;
        }
        .stTextInput>div>div>input {
            background-color: #333 !important;
            color: #E1E1E1 !important;
        }
        .stSelectbox>div>div>div {
            background-color: #333 !important;
            color: #E1E1E1 !important;
        }
    }
    
    /* Custom styling for plots to ensure visibility in dark mode */
    .js-plotly-plot .plotly .modebar {
        background-color: transparent !important;
    }
    
    /* Ensure expandable sections are visible in dark mode */
    .streamlit-expanderHeader {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'current_graph' not in st.session_state:
    st.session_state.current_graph = None
if 'current_book_metadata' not in st.session_state:
    st.session_state.current_book_metadata = None
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = ""
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'current_book_name' not in st.session_state:
    st.session_state.current_book_name = ""
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""

# Load embedding model on startup
load_embedding_model()

# Define the main app
def main():
    # Display MagicBook header
    st.markdown('<div class="main-header">📚 MagicBook</div>', unsafe_allow_html=True)
    st.markdown('### Dynamic Book Relationship Visualization System')
    st.markdown('Explore the intricate network of characters, locations, events, and more from your favorite books.')
    
    # Create tabs for the app
    tabs = st.tabs(["Book Selection", "Graph Visualization", "Entity Explorer", "Analysis", "Settings"])
    
    # Book Selection Tab
    with tabs[0]:
        book_selection_tab()
    
    # Graph Visualization Tab
    with tabs[1]:
        graph_visualization_tab()
    
    # Entity Explorer Tab
    with tabs[2]:
        entity_explorer_tab()
    
    # Analysis Tab
    with tabs[3]:
        analysis_tab()
    
    # Settings Tab
    with tabs[4]:
        settings_tab()
    
    # Show footer
    st.markdown("---")
    st.markdown("MagicBook - Created with ❤️ for book lovers and data visualization enthusiasts")

def book_selection_tab():
    """Book Selection Tab Content"""
    st.markdown("## Choose a Book")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Load Cached Book")
        
        # Display cached books in a dropdown
        cached_books = get_cached_book_list()
        selected_book = st.selectbox("Select a cached book:", cached_books)
        
        if st.button("Load Book", key="load_cached_book_btn"):
            if selected_book == "No cached books found":
                st.error("No cached books available. Please upload a new book.")
            else:
                load_book(selected_book)
    
    with col2:
        st.markdown("### 📄 Upload New Book")
        
        uploaded_file = st.file_uploader("Upload PDF Book", type=["pdf"])
        
        if uploaded_file:
            book_name = st.text_input("Book Name", 
                                     value=uploaded_file.name.replace(".pdf", ""))
            
            if st.button("Process Book", key="process_book_btn"):
                # Define the function to run async task
                def run_async_function():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(process_uploaded_book(uploaded_file, book_name))
                    finally:
                        loop.close()
                
                # Set processing state
                st.session_state.is_processing = True
                st.session_state.processing_status = "Starting book processing..."
                
                # Start the thread
                threading.Thread(target=run_async_function).start()


    # Display current status
    if st.session_state.current_book_metadata:
        st.success(f"Current book: {st.session_state.current_book_metadata.book_name}")
        with st.expander("Book Details", expanded=False):
            st.write(st.session_state.current_book_metadata)
    
    # Show processing status or error message if any
    if st.session_state.is_processing:
        st.info(st.session_state.processing_status)
    
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        if st.button("Clear Error"):
            st.session_state.error_message = ""

def graph_visualization_tab():
    """Graph Visualization Tab Content"""
    st.markdown("## Book Graph Visualization")
    
    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return
    
    st.markdown(f"### Visualizing: {st.session_state.current_book_metadata.book_name}")
    
    # Display the graph visualization
    if st.session_state.current_graph:
        graph_fig = create_interactive_visualization(
            st.session_state.current_graph, 
            st.session_state.current_book_metadata.book_name
        )
        
        if graph_fig:
            st.plotly_chart(graph_fig, use_container_width=True)
        else:
            st.error("Error creating visualization")
            
        # Display graph statistics
        with st.expander("Graph Statistics", expanded=False):
            st.write(f"**Nodes:** {st.session_state.current_graph.number_of_nodes()}")
            st.write(f"**Edges:** {st.session_state.current_graph.number_of_edges()}")
            
            # Display node types and counts
            node_types = {}
            for node, attrs in st.session_state.current_graph.nodes(data=True):
                entity_type = attrs.get('entity_type', 'Unknown')
                if entity_type not in node_types:
                    node_types[entity_type] = 0
                node_types[entity_type] += 1
            
            st.write("**Node Types:**")
            node_types_df = pd.DataFrame({
                'Type': list(node_types.keys()),
                'Count': list(node_types.values())
            }).sort_values(by='Count', ascending=False)
            
            st.dataframe(node_types_df)
            
            # Display edge types and counts
            edge_types = {}
            for _, _, attrs in st.session_state.current_graph.edges(data=True):
                rel_type = attrs.get('type', 'Unknown')
                if rel_type not in edge_types:
                    edge_types[rel_type] = 0
                edge_types[rel_type] += 1
            
            st.write("**Relationship Types:**")
            edge_types_df = pd.DataFrame({
                'Type': list(edge_types.keys()),
                'Count': list(edge_types.values())
            }).sort_values(by='Count', ascending=False)
            
            st.dataframe(edge_types_df)
    else:
        st.warning("Graph not available. There might be an error in processing the book.")

def entity_explorer_tab():
    """Entity Explorer Tab Content"""
    st.markdown("## Entity Explorer")
    
    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return
    
    book_metadata = st.session_state.current_book_metadata
    
    if not book_metadata.entities_map or not book_metadata.relationships_map:
        st.warning("No entities or relationships found in this book.")
        return
    
    # Display entity navigation sidebar
    entity_type = st.selectbox(
        "Select Entity Type:",
        options=list(book_metadata.entities_map.keys())
    )
    
    # Display entities of selected type
    if entity_type and entity_type in book_metadata.entities_map:
        entities = book_metadata.entities_map[entity_type]
        
        # Show entity list
        st.markdown(f"### {entity_type}s ({len(entities)})")
        
        # Create a dataframe for better display
        entity_data = []
        for entity in entities:
            entry = {
                'Key': entity.get('_key', ''),
                'Name': entity.get('name', 'Unknown')
            }
            
            # Add additional common fields based on entity type
            if entity_type == 'CHARACTER':
                entry['Significance'] = entity.get('significance', '')
                entry['Gender'] = entity.get('gender', '')
            elif entity_type == 'LOCATION':
                entry['Type'] = entity.get('type', '')
                entry['Region'] = entity.get('region', '')
            elif entity_type == 'EVENT':
                entry['Type'] = entity.get('type', '')
            
            entity_data.append(entry)
        
        # Display as a table with filtering
        if entity_data:
            entity_df = pd.DataFrame(entity_data)
            st.dataframe(entity_df)
            
            # Entity details view
            selected_entity_key = st.selectbox(
                "Select an entity to view details:",
                options=[e['Key'] for e in entity_data],
                format_func=lambda x: next((e['Name'] for e in entity_data if e['Key'] == x), x)
            )
            
            if selected_entity_key:
                selected_entity = next((e for e in entities if e.get('_key') == selected_entity_key), None)
                
                if selected_entity:
                    st.markdown(f"### Details for: {selected_entity.get('name', 'Unknown')}")
                    
                    # Show all attributes as a table
                    st.json(selected_entity)
                    
                    # Show relationships involving this entity
                    st.markdown("### Relationships")
                    
                    if st.session_state.current_graph:
                        # Get incoming edges
                        incoming_edges = []
                        for source, target, attrs in st.session_state.current_graph.in_edges(selected_entity_key, data=True):
                            source_node = st.session_state.current_graph.nodes[source]
                            incoming_edges.append({
                                'Source': source_node.get('name', source),
                                'Source Type': source_node.get('entity_type', 'Unknown'),
                                'Relationship': attrs.get('type', 'Unknown'),
                                'Details': str({k: v for k, v in attrs.items() if k != 'type'})
                            })
                        
                        # Get outgoing edges
                        outgoing_edges = []
                        for source, target, attrs in st.session_state.current_graph.out_edges(selected_entity_key, data=True):
                            target_node = st.session_state.current_graph.nodes[target]
                            outgoing_edges.append({
                                'Target': target_node.get('name', target),
                                'Target Type': target_node.get('entity_type', 'Unknown'),
                                'Relationship': attrs.get('type', 'Unknown'),
                                'Details': str({k: v for k, v in attrs.items() if k != 'type'})
                            })
                        
                        # Display relationships
                        if incoming_edges:
                            st.markdown("#### Incoming Relationships")
                            st.dataframe(pd.DataFrame(incoming_edges))
                        
                        if outgoing_edges:
                            st.markdown("#### Outgoing Relationships")
                            st.dataframe(pd.DataFrame(outgoing_edges))
                        
                        if not incoming_edges and not outgoing_edges:
                            st.info("No relationships found for this entity.")
        else:
            st.info(f"No {entity_type} entities found in this book.")

def analysis_tab():
    """Analysis Tab Content"""
    st.markdown("## Book Analysis")
    
    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return
    
    book_metadata = st.session_state.current_book_metadata
    
    # Create tabs for different analyses
    analysis_tabs = st.tabs(["Entity Analysis", "Relationship Analysis", "Network Analysis", "Text View"])
    
    # Entity Analysis Tab
    with analysis_tabs[0]:
        st.markdown("### Entity Analysis")
        
        if book_metadata.entities_map:
            # Analyze entities
            entity_analysis = analyze_book_entities(book_metadata.entities_map)
            
            if entity_analysis:
                # Create pie chart of entity types
                if 'entity_counts' in entity_analysis:
                    entity_types = list(entity_analysis['entity_counts'].keys())
                    entity_counts = list(entity_analysis['entity_counts'].values())
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=entity_types,
                        values=entity_counts,
                        hole=.3,
                        marker_colors=['#3357FF', '#33FFF5', '#A64DFF', '#F5FF33', 
                                     '#FF5733', '#FF33A8', '#8C8C8C', '#33FF57']
                    )])
                    
                    fig.update_layout(
                        title="Entity Type Distribution",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display main characters
                if 'main_characters' in entity_analysis and entity_analysis['main_characters']:
                    st.markdown("#### Main Characters")
                    for character in entity_analysis['main_characters']:
                        st.markdown(f"**{character['name']}**: {character['description']}")
                
                # Display main locations
                if 'main_locations' in entity_analysis and entity_analysis['main_locations']:
                    st.markdown("#### Key Locations")
                    for location in entity_analysis['main_locations']:
                        st.markdown(f"**{location['name']}**: {location['description']}")
                
                # Display key events
                if 'key_events' in entity_analysis and entity_analysis['key_events']:
                    st.markdown("#### Key Events")
                    for event in entity_analysis['key_events']:
                        st.markdown(f"**{event['name']}**: {event['summary']}")
            else:
                st.warning("No entity analysis available.")
        else:
            st.warning("No entities found in this book.")
    
    # Relationship Analysis Tab
    with analysis_tabs[1]:
        st.markdown("### Relationship Analysis")
        
        if book_metadata.relationships_map:
            # Analyze relationships
            relationship_analysis = analyze_book_relationships(book_metadata.relationships_map)
            
            if relationship_analysis:
                # Create bar chart of relationship types
                if 'relationship_counts' in relationship_analysis:
                    rel_types = list(relationship_analysis['relationship_counts'].keys())
                    rel_counts = list(relationship_analysis['relationship_counts'].values())
                    
                    # If there are too many types, limit to top 10
                    if len(rel_types) > 10:
                        sorted_indices = sorted(range(len(rel_counts)), key=lambda i: rel_counts[i], reverse=True)[:10]
                        rel_types = [rel_types[i] for i in sorted_indices]
                        rel_counts = [rel_counts[i] for i in sorted_indices]
                    
                    fig = go.Figure(data=[go.Bar(
                        x=rel_types,
                        y=rel_counts,
                        marker_color='#4c78a8'
                    )])
                    
                    fig.update_layout(
                        title="Relationship Type Distribution",
                        xaxis_title="Relationship Type",
                        yaxis_title="Count",
                        height=500,
                        xaxis=dict(tickangle=-45)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display key relationship types
                if 'key_relationship_types' in relationship_analysis:
                    st.markdown("#### Key Relationship Types")
                    for rel in relationship_analysis['key_relationship_types']:
                        st.markdown(f"**{rel['type']}**: {rel['count']} relationships")
            else:
                st.warning("No relationship analysis available.")
        else:
            st.warning("No relationships found in this book.")
    
    # Network Analysis Tab
    with analysis_tabs[2]:
        st.markdown("### Network Analysis")
        
        if st.session_state.current_graph:
            G = st.session_state.current_graph
            
            # Display graph statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Statistics")
                st.write(f"**Nodes:** {G.number_of_nodes()}")
                st.write(f"**Edges:** {G.number_of_edges()}")
                st.write(f"**Density:** {nx.density(G):.4f}")
                
                if nx.is_directed(G):
                    st.write(f"**Strongly Connected Components:** {len(list(nx.strongly_connected_components(G)))}")
                    st.write(f"**Weakly Connected Components:** {len(list(nx.weakly_connected_components(G)))}")
                else:
                    st.write(f"**Connected Components:** {nx.number_connected_components(G)}")
            
            with col2:
                st.markdown("#### Centrality Measures")
                
                # Calculate degree centrality for top nodes
                degree_centrality = nx.degree_centrality(G)
                top_degree_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
                
                st.markdown("**Top 5 Nodes by Degree Centrality:**")
                for node_id, centrality in top_degree_nodes:
                    node_name = G.nodes[node_id].get('name', node_id)
                    st.write(f"- {node_name}: {centrality:.4f}")
                
                # Calculate betweenness centrality if not too computationally expensive
                if G.number_of_nodes() <= 500:  # Limit to smaller graphs
                    try:
                        betweenness_centrality = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
                        top_betweenness_nodes = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
                        
                        st.markdown("**Top 5 Nodes by Betweenness Centrality:**")
                        for node_id, centrality in top_betweenness_nodes:
                            node_name = G.nodes[node_id].get('name', node_id)
                            st.write(f"- {node_name}: {centrality:.4f}")
                    except Exception as e:
                        st.write("Betweenness centrality calculation failed.")
            
            # Advanced network analysis
            with st.expander("Advanced Network Analysis", expanded=False):
                st.write("This section contains computationally intensive analyses.")
                
                if st.button("Calculate Community Structure"):
                    try:
                        with st.spinner("Calculating communities..."):
                            # Use a simple community detection algorithm
                            if nx.is_directed(G):
                                communities = nx.community.greedy_modularity_communities(G.to_undirected())
                            else:
                                communities = nx.community.greedy_modularity_communities(G)
                            
                            st.write(f"**Found {len(communities)} communities**")
                            
                            # Display the top 5 largest communities
                            for i, community in enumerate(list(communities)[:5]):
                                community_nodes = list(community)
                                node_names = [G.nodes[node].get('name', node) for node in community_nodes[:5]]
                                st.write(f"Community {i+1} ({len(community_nodes)} nodes): {', '.join(node_names)}...")
                    except Exception as e:
                        st.error(f"Error calculating communities: {str(e)}")
        else:
            st.warning("No graph available for analysis.")
    
    # Text View Tab
    with analysis_tabs[3]:
        st.markdown("### Text Representation")
        
        if book_metadata.entities_map and book_metadata.relationships_map:
            # Display tree representation
            tree_text = create_tree_display(book_metadata.entities_map, book_metadata.relationships_map)
            st.text(tree_text)
        else:
            st.warning("No entities or relationships available for text view.")

def settings_tab():
    """Settings Tab Content"""
    st.markdown("## Settings")
    
    # Database Connection Settings
    st.markdown("### Database Connection")
    
    db_url = st.text_input("Database URL", value=os.environ.get('DATABASE_HOST', ''))
    db_username = st.text_input("Database Username", value=os.environ.get('DATABASE_USERNAME', ''))
    db_password = st.text_input("Database Password", value=os.environ.get('DATABASE_PASSWORD', ''), type="password")
    
    if st.button("Test Connection"):
        # Update environment variables
        os.environ['DATABASE_HOST'] = db_url
        os.environ['DATABASE_USERNAME'] = db_username
        os.environ['DATABASE_PASSWORD'] = db_password
        
        # Test connection
        if is_db_connected():
            st.success("Successfully connected to database!")
        else:
            st.error("Failed to connect to database. Please check your settings.")
    
    # ArangoDB Integration
    st.markdown("### ArangoDB Integration")
    
    if st.session_state.current_book_metadata and st.session_state.current_graph:
        if st.button("Upload to ArangoDB"):
            book_name = st.session_state.current_book_metadata.book_name
            with st.spinner(f"Uploading graph for '{book_name}' to ArangoDB..."):
                db_graph = create_arango_graph(st.session_state.current_graph, book_name)
                
                if db_graph:
                    st.success(f"Successfully uploaded graph for '{book_name}' to ArangoDB!")
                else:
                    st.error("Failed to upload graph to ArangoDB.")
    else:
        st.info("Please load a book to enable ArangoDB integration.")
    
    # Cache Management
    st.markdown("### Cache Management")
    
    # List cached books
    cached_books = get_cached_book_list()
    if cached_books and cached_books[0] != "No cached books found":
        book_to_delete = st.selectbox("Select a book to delete from cache:", cached_books)
        
        if st.button("Delete from Cache"):
            if delete_cached_book(book_to_delete):
                st.success(f"Successfully deleted '{book_to_delete}' from cache.")
                if st.session_state.current_book_metadata and st.session_state.current_book_metadata.book_name == book_to_delete:
                    st.session_state.current_book_metadata = None
                    st.session_state.current_graph = None
                    st.session_state.current_book_name = ""
                    st.warning("Current book was deleted from cache. Please load another book.")
                    
                # Refresh cached books list
                st.experimental_rerun()
            else:
                st.error(f"Failed to delete '{book_to_delete}' from cache.")
    else:
        st.info("No cached books found.")
    
    # Clear All Cache
    if st.button("Clear All Cache"):
        data_dir = Path("data")
        if data_dir.exists():
            try:
                # Delete all subdirectories in data directory
                for subdir in data_dir.iterdir():
                    if subdir.is_dir():
                        for file in subdir.iterdir():
                            file.unlink()
                        subdir.rmdir()
                
                # Reset session state
                st.session_state.current_book_metadata = None
                st.session_state.current_graph = None
                st.session_state.current_book_name = ""
                
                st.success("Successfully cleared all cache.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to clear cache: {str(e)}")
        else:
            st.info("No cache directory found.")

# Helper functions for the UI

def load_book(book_name):
    """Load a book from cache by name"""
    try:
        book_metadata = select_cached_book(book_name)
        
        if not book_metadata:
            st.session_state.error_message = f"Error: Book '{book_name}' not found in cache."
            return
        
        # Create graph from book metadata
        graph = create_graph_from_book_metadata(book_metadata)
        
        if not graph:
            st.session_state.error_message = "Error: Failed to create graph from book metadata."
            return
        
        # Update session state
        st.session_state.current_book_metadata = book_metadata
        st.session_state.current_graph = graph
        st.session_state.current_book_name = book_name
        st.session_state.error_message = ""
        
        # Show success message
        st.success(f"Successfully loaded book: {book_name}")
    except Exception as e:
        st.session_state.error_message = f"Error loading book: {str(e)}"

async def process_uploaded_book(uploaded_file, book_name):
    """Process an uploaded PDF book"""
    if not uploaded_file:
        st.session_state.error_message = "Error: No file uploaded."
        return
    
    # Save uploaded file temporarily
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Set processing state
    st.session_state.is_processing = True
    st.session_state.processing_status = "Extracting text from PDF..."
    
    try:
        # Extract text from PDF
        book_text = extract_text_from_pdf(temp_file_path)
        
        if isinstance(book_text, str) and book_text.startswith("Error"):
            st.session_state.error_message = book_text
            st.session_state.is_processing = False
            os.remove(temp_file_path)
            return
        
        # Update status
        st.session_state.processing_status = "Creating dummy book metadata and graph for demo purposes..."
        
        # Create graph from entities and relationships
        graph_metadata = await create_graph_from_text(book_text)  # Make sure 'await' is here
        
        if not graph_metadata:
            st.session_state.error_message = "Error: Failed to create graph from book metadata."
            st.session_state.is_processing = False
            os.remove(temp_file_path)
            return
        
        # Save book metadata to cache
        if save_book_metadata(graph_metadata[1]):
            st.session_state.processing_status = "Book processed and saved to cache."
        else:
            st.session_state.processing_status = "Book processed but failed to save to cache."
        
        # Update session state
        st.session_state.current_book_metadata = graph_metadata[1]
        st.session_state.current_graph = graph_metadata[0]
        st.session_state.current_book_name = book_name
        st.session_state.error_message = ""
        
        # Clean up
        os.remove(temp_file_path)
        
        # Show success message
        st.success(f"Successfully processed book: {book_name}")
    except Exception as e:
        st.session_state.error_message = f"Error processing book: {str(e)}"
    finally:
        st.session_state.is_processing = False

# Run the app
if __name__ == "__main__":
    main()