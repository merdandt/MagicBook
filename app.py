# ... (imports and other code remain the same) ...

import time
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

ctx = get_script_run_ctx()
if ctx is None or ctx._set_page_config_allowed:      # ← not set yet
    st.set_page_config(page_title="MagicBook",
                       page_icon="📚",
                       layout="wide")

# logging setup AFTER page_config
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# live log placeholder
log_placeholder = st.sidebar.empty()

class StreamlitHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))
        self.lines = self.lines[-200:]
        self.placeholder.code("\n".join(self.lines), language="")

handler = StreamlitHandler(log_placeholder)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(handler)

import networkx as nx
import pandas as pd
import os
import logging
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime


try:
    from utils.file_utils import extract_text_from_pdf
    from utils.embedding import load_embedding_model
    from model.book_metadata import BookMetadata # Assuming this class definition exists
    from services.cache_service import (load_cached_books, get_cached_book_list,
                                       select_cached_book, save_book_metadata,
                                       delete_cached_book)
    from services.graph_service import (create_graph_from_book_metadata, create_graph_from_text,
                                       create_interactive_visualization,
                                       analyze_book_entities, analyze_book_relationships)
    from services.db_service import is_db_connected, create_arango_graph
    from core.visualizer import create_tree_display
except ImportError as e:
    st.error(f"Error importing local modules: {e}. Make sure the modules are in the correct path.")
    # You might want to exit or handle this more gracefully
    st.stop()


import warnings

# Filter out the torch.classes warning
warnings.filterwarnings("ignore", message="Examining the path of torch.classes")


# Custom CSS with dark mode support (remains the same)
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
/* ---- Add this block (or merge with the one you already have) ---- */
.stTabs [data-baseweb="tab"]{
    /* existing declarations …                                */
    height: 50px;
    white-space: pre-wrap;
    border-radius: 4px 4px 0 0;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;

    /* NEW: horizontal spacing */
    padding-left: 18px;   /* or whatever looks good */
    padding-right: 18px;
}

/* optional: if you only want the text, not the whole tab, spaced */
.stTabs [data-baseweb="tab"] > div               /* BaseWeb wraps text    */
{
    margin-left: 6px;      /* space before label  */
    margin-right: 6px;     /* space after label   */
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
if 'current_book_name' not in st.session_state:
    st.session_state.current_book_name = ""
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""

# Load embedding model on startup
with st.spinner("Loading embedding model..."):
    try:
        load_embedding_model()
        logger.info("Embedding model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}", exc_info=True)
        st.error(f"Fatal Error: Failed to load embedding model: {e}")
        st.stop() # Stop the app if model fails to load

def update_status(message):
    """Callback to update the status in session state and log."""
    logger.info(f"Status Update: {message}")
    st.session_state.processing_status = message

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
        cached_books = get_cached_book_list()

        if not cached_books or cached_books[0] == "No cached books found":
            st.info("No cached books found. Upload a new book to get started.")
        else:
            # Use session state to preserve selection across reruns if needed
            if 'selected_cached_book' not in st.session_state:
                st.session_state.selected_cached_book = cached_books[0]

            selected_book = st.selectbox(
                "Select a book from cache:",
                cached_books,
                key="sb_cached_books",
                index=cached_books.index(st.session_state.selected_cached_book) if st.session_state.selected_cached_book in cached_books else 0
            )
            st.session_state.selected_cached_book = selected_book # Update state on change

            if st.button("Load Book", key="load_book_btn"):
                if selected_book:
                    with st.spinner(f"Loading '{selected_book}'..."):
                        load_book(selected_book) # Call the loading function directly
                        # No st.rerun() needed here, spinner context manager handles UI update exit
                else:
                    st.warning("Please select a book to load.")


    with col2:
        st.markdown("### 📄 Upload New Book")
        uploaded_file = st.file_uploader("Upload PDF Book", type=["pdf"])

        if uploaded_file:
            default_book_name = Path(uploaded_file.name).stem # Use pathlib for cleaner name extraction
            book_name = st.text_input("Book Name", value=default_book_name)

            if st.button("Process Book", key="process_book_btn"):
                if not book_name:
                    st.error("Please enter a name for the book.")
                else:
                    # --- SYNCHRONOUS PROCESSING ---
                    st.session_state.processing_status = "Initializing processing..."
                    st.session_state.error_message = "" # Clear previous errors

                    # Use st.spinner for visual feedback during the synchronous operation
                    with st.spinner(st.session_state.processing_status):
                        # Directly call the processing function. It will block until done.
                        # The update_status callback will update the spinner text.
                        process_uploaded_book(uploaded_file, book_name, update_status)

                    # After process_uploaded_book finishes (or raises an error),
                    # the st.rerun() call inside its finally block will refresh the UI.

    # Display current status or error message
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        # Add a button to clear the error manually if needed
        if st.button("Clear Error Message"):
            st.session_state.error_message = ""
            st.rerun()

    if st.session_state.current_book_metadata:
        st.success(f"Current book loaded: **{st.session_state.current_book_metadata.book_name}**")
        with st.expander("Book Details", expanded=False):
            # Check attributes before accessing them
            if hasattr(st.session_state.current_book_metadata, 'file_name') and st.session_state.current_book_metadata.file_name:
                 st.write(f"**Original File:** {st.session_state.current_book_metadata.file_name}")

            # --- ADDED CHECK for processing_date ---
            if hasattr(st.session_state.current_book_metadata, 'processing_date') and st.session_state.current_book_metadata.processing_date:
                st.write(f"**Processing Date:** {st.session_state.current_book_metadata.processing_date}")
            else:
                st.write("**Processing Date:** Not available") # Fallback

            entity_map = getattr(st.session_state.current_book_metadata, 'entities_map', None)
            rel_map = getattr(st.session_state.current_book_metadata, 'relationships_map', None)

            st.write(f"**Entity Types Found:** {len(entity_map) if entity_map else 0}")
            total_entities = sum(len(v) for v in entity_map.values()) if entity_map else 0
            st.write(f"**Total Entities:** {total_entities}")

            st.write(f"**Relationship Types Found:** {len(rel_map) if rel_map else 0}")
            total_relationships = sum(len(v) for v in rel_map.values()) if rel_map else 0
            st.write(f"**Total Relationships:** {total_relationships}")

    elif not st.session_state.error_message: # Don't show info if an error is displayed
        st.info("Upload a new book or load one from the cache.")


# ... (graph_visualization_tab remains the same) ...
def graph_visualization_tab():
    """Graph Visualization Tab Content"""
    st.markdown("## Book Graph Visualization")

    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return

    st.markdown(f"### Visualizing: {st.session_state.current_book_metadata.book_name}")

    # Display the graph visualization
    if st.session_state.current_graph:
        # Check if graph is empty
        if st.session_state.current_graph.number_of_nodes() == 0:
             st.warning("The graph for this book is empty. Cannot generate visualization.")
             return

        try:
            with st.spinner("Generating graph visualization..."):
                graph_fig = create_interactive_visualization(
                    st.session_state.current_graph,
                    st.session_state.current_book_metadata.book_name
                )

            if graph_fig:
                st.plotly_chart(graph_fig, use_container_width=True)
            else:
                st.error("Could not create visualization. The graph might be invalid or generation failed.")

            # Display graph statistics
            with st.expander("Graph Statistics", expanded=False):
                st.write(f"**Nodes:** {st.session_state.current_graph.number_of_nodes()}")
                st.write(f"**Edges:** {st.session_state.current_graph.number_of_edges()}")

                # Display node types and counts
                node_types = {}
                for _, attrs in st.session_state.current_graph.nodes(data=True):
                    entity_type = attrs.get('entity_type', 'Unknown')
                    node_types[entity_type] = node_types.get(entity_type, 0) + 1

                st.write("**Node Types:**")
                if node_types:
                    node_types_df = pd.DataFrame({
                        'Type': list(node_types.keys()),
                        'Count': list(node_types.values())
                    }).sort_values(by='Count', ascending=False)
                    st.dataframe(node_types_df)
                else:
                    st.write("No nodes found.")

                # Display edge types and counts
                edge_types = {}
                for _, _, attrs in st.session_state.current_graph.edges(data=True):
                    rel_type = attrs.get('type', 'Unknown')
                    edge_types[rel_type] = edge_types.get(rel_type, 0) + 1

                st.write("**Relationship Types:**")
                if edge_types:
                    edge_types_df = pd.DataFrame({
                        'Type': list(edge_types.keys()),
                        'Count': list(edge_types.values())
                    }).sort_values(by='Count', ascending=False)
                    st.dataframe(edge_types_df)
                else:
                    st.write("No edges found.")

        except Exception as e:
            logger.error(f"Error generating visualization or stats: {e}", exc_info=True)
            st.error(f"An error occurred during graph visualization: {e}")

    else:
        st.warning("Graph not available. Please process the book again or load a valid one.")

# ... (entity_explorer_tab remains the same) ...
def entity_explorer_tab():
    """Entity Explorer Tab Content"""
    st.markdown("## Entity Explorer")

    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return

    book_metadata = st.session_state.current_book_metadata
    # Use getattr for safer access to potentially missing attributes
    entities_map = getattr(book_metadata, 'entities_map', None)

    if not entities_map:
        st.warning("No entities found in this book's metadata.")
        return

    # Use a sidebar for selection if there are many types, otherwise use selectbox
    entity_types_list = sorted(list(entities_map.keys()))
    if not entity_types_list:
         st.warning("No entity types found.")
         return

    selector_location = st.sidebar if len(entity_types_list) > 5 else st
    if len(entity_types_list) > 5:
        selector_location.markdown("### Entity Selection")

    entity_type = selector_location.selectbox(
        "Select Entity Type:",
        options=entity_types_list,
        key=f"entity_type_{'sidebar' if len(entity_types_list) > 5 else 'main'}_selector"
    )

    # Display entities of selected type
    if entity_type and entity_type in entities_map:
        entities = entities_map[entity_type]
        st.markdown(f"### {entity_type}s ({len(entities)})")

        if not entities:
            st.info(f"No entities of type '{entity_type}' found.")
            return

        entity_data = []
        try:
            for entity in entities:
                # Basic info common to all entities
                entry = {
                    'Key': entity.get('_key', 'N/A'),
                    'Name': entity.get('name', 'Unknown')
                }
                # Add type-specific common fields, checking if they exist
                if entity_type == 'CHARACTER':
                    entry['Significance'] = entity.get('significance')
                    entry['Gender'] = entity.get('gender')
                elif entity_type == 'LOCATION':
                    entry['Type'] = entity.get('type')
                    entry['Region'] = entity.get('region')
                elif entity_type == 'EVENT':
                    entry['Type'] = entity.get('type')
                    entry['Importance'] = entity.get('importance') # Example field

                # Include other non-null attributes dynamically? Maybe too complex for now.
                # entry.update({k: v for k, v in entity.items() if k not in entry and v is not None})

                entity_data.append(entry)

            if entity_data:
                entity_df = pd.DataFrame(entity_data)
                # Display dataframe, maybe filter columns with all NAs
                entity_df = entity_df.dropna(axis=1, how='all')
                st.dataframe(entity_df, use_container_width=True)

                # Entity details view - Allow selection from the table
                # Create unique labels for selection even if names are duplicated
                entity_options = {f"{e['Name']} ({e['Key']})": e['Key'] for e in entity_data}
                # Handle cases where entity_options might be empty (though unlikely if entity_data is not)
                if not entity_options:
                    st.info("No entities available for detailed view.")
                    return

                selected_entity_label = st.selectbox(
                    "Select an entity to view details:",
                    options=list(entity_options.keys()), # Ensure it's a list
                    index=0 # Default to the first one
                )

                if selected_entity_label:
                    selected_entity_key = entity_options[selected_entity_label]
                    # Find the entity dict again
                    selected_entity = next((e for e in entities if e.get('_key') == selected_entity_key), None)

                    if selected_entity:
                        st.markdown(f"#### Details for: {selected_entity.get('name', 'Unknown')}")
                        # Show all attributes cleanly
                        st.json(selected_entity, expanded=False) # Use json view, maybe expandable

                        # Show relationships involving this entity if graph exists
                        st.markdown("#### Relationships")
                        current_graph = st.session_state.get('current_graph') # Use .get for safety
                        if current_graph and selected_entity_key in current_graph:
                            G = current_graph
                            incoming_edges_data = []
                            outgoing_edges_data = []

                            # Incoming Edges
                            for source, target, attrs in G.in_edges(selected_entity_key, data=True):
                                source_node = G.nodes.get(source, {})
                                incoming_edges_data.append({
                                    'Source': source_node.get('name', source),
                                    'Source Type': source_node.get('entity_type', 'Unknown'),
                                    'Relationship': attrs.get('type', 'related'),
                                    'Details': str({k: v for k, v in attrs.items() if k not in ['type', 'id', 'source', 'target']}) # Clean up details further
                                })

                            # Outgoing Edges
                            for source, target, attrs in G.out_edges(selected_entity_key, data=True):
                                target_node = G.nodes.get(target, {})
                                outgoing_edges_data.append({
                                    'Target': target_node.get('name', target),
                                    'Target Type': target_node.get('entity_type', 'Unknown'),
                                    'Relationship': attrs.get('type', 'related'),
                                    'Details': str({k: v for k, v in attrs.items() if k not in ['type', 'id', 'source', 'target']}) # Clean up details further
                                })

                            if incoming_edges_data:
                                st.markdown("**Incoming Relationships**")
                                st.dataframe(pd.DataFrame(incoming_edges_data), use_container_width=True, hide_index=True)
                            if outgoing_edges_data:
                                st.markdown("**Outgoing Relationships**")
                                st.dataframe(pd.DataFrame(outgoing_edges_data), use_container_width=True, hide_index=True)

                            if not incoming_edges_data and not outgoing_edges_data:
                                st.info("No relationships found for this entity in the graph.")
                        elif not current_graph:
                             st.info("Graph not loaded, cannot display relationships.")
                        else:
                             st.info(f"Entity key '{selected_entity_key}' not found in the graph nodes.")
                    else:
                        st.warning(f"Could not find details for entity key: {selected_entity_key}")
            else:
                 st.info(f"No data processed for entities of type '{entity_type}'.")

        except Exception as e:
            logger.error(f"Error displaying entities of type {entity_type}: {e}", exc_info=True)
            st.error(f"An error occurred while displaying entity details: {e}")

# ... (analysis_tab remains the same) ...
def analysis_tab():
    """Analysis Tab Content"""
    st.markdown("## Book Analysis")

    if not st.session_state.current_book_metadata:
        st.info("Please select or upload a book first.")
        return

    book_metadata = st.session_state.current_book_metadata
    entities_map = getattr(book_metadata, 'entities_map', None)
    relationships_map = getattr(book_metadata, 'relationships_map', None)
    current_graph = st.session_state.get('current_graph')

    # Create tabs for different analyses
    analysis_tabs = st.tabs(["Entity Analysis", "Relationship Analysis", "Network Analysis", "Text View"])

    # Entity Analysis Tab
    with analysis_tabs[0]:
        st.markdown("### Entity Analysis")

        if not entities_map:
            st.warning("No entities found for analysis.")
        else:
            try:
                with st.spinner("Analyzing entities..."):
                    entity_analysis = analyze_book_entities(entities_map) # Pass the map

                if not entity_analysis:
                    st.warning("Entity analysis did not return results.")
                else:
                    # Create pie chart of entity types
                    if 'entity_counts' in entity_analysis and entity_analysis['entity_counts']:
                        entity_types = list(entity_analysis['entity_counts'].keys())
                        entity_counts = list(entity_analysis['entity_counts'].values())

                        fig_entity_pie = go.Figure(data=[go.Pie(
                            labels=entity_types,
                            values=entity_counts,
                            hole=.3,
                            pull=[0.05] * len(entity_types) # Slightly pull slices
                        )])
                        fig_entity_pie.update_layout(
                            title_text="Entity Type Distribution",
                            height=450,
                            margin=dict(t=50, b=0, l=0, r=0), # Adjust margins
                            legend_title_text="Entity Types"
                        )
                        st.plotly_chart(fig_entity_pie, use_container_width=True)
                    else:
                        st.info("No entity count data available for chart.")

                    # Display main characters/locations/events if available
                    for key, title in [('main_characters', 'Main Characters'),
                                       ('main_locations', 'Key Locations'),
                                       ('key_events', 'Key Events')]:
                        if key in entity_analysis and entity_analysis[key]:
                            st.markdown(f"#### {title}")
                            # Format display nicely, perhaps as a list or table
                            items_df = pd.DataFrame(entity_analysis[key])
                            st.dataframe(items_df, use_container_width=True, hide_index=True)

            except Exception as e:
                logger.error(f"Error during entity analysis: {e}", exc_info=True)
                st.error(f"An error occurred during entity analysis: {e}")


    # Relationship Analysis Tab
    with analysis_tabs[1]:
        st.markdown("### Relationship Analysis")

        if not relationships_map:
            st.warning("No relationships found for analysis.")
        else:
            try:
                with st.spinner("Analyzing relationships..."):
                    relationship_analysis = analyze_book_relationships(relationships_map) # Pass the map

                if not relationship_analysis:
                    st.warning("Relationship analysis did not return results.")
                else:
                    # Create bar chart of relationship types
                    if 'relationship_counts' in relationship_analysis and relationship_analysis['relationship_counts']:
                        rel_counts_dict = relationship_analysis['relationship_counts']
                        # Sort by count descending
                        sorted_rels = sorted(rel_counts_dict.items(), key=lambda item: item[1], reverse=True)

                        # Limit number of types shown for clarity, e.g., top 15
                        top_n = 15
                        rel_types = [item[0] for item in sorted_rels[:top_n]]
                        rel_counts = [item[1] for item in sorted_rels[:top_n]]

                        if rel_types:
                            fig_rel_bar = go.Figure(data=[go.Bar(
                                x=rel_types,
                                y=rel_counts,
                                marker_color='#4c78a8' # Example color
                            )])
                            fig_rel_bar.update_layout(
                                title_text=f"Top {len(rel_types)} Relationship Types by Frequency",
                                xaxis_title="Relationship Type",
                                yaxis_title="Count",
                                height=450,
                                xaxis_tickangle=-45,
                                margin=dict(t=50, b=100, l=0, r=0) # Adjust margins for labels
                            )
                            st.plotly_chart(fig_rel_bar, use_container_width=True)
                        else:
                            st.info("No relationship count data available for chart.")
                    else:
                         st.info("Relationship count data not found in analysis results.")

                    # Display key relationship types summary if available
                    if 'key_relationship_types' in relationship_analysis and relationship_analysis['key_relationship_types']:
                        st.markdown("#### Key Relationship Types Summary")
                        key_rels_df = pd.DataFrame(relationship_analysis['key_relationship_types'])
                        st.dataframe(key_rels_df, use_container_width=True, hide_index=True)

            except Exception as e:
                logger.error(f"Error during relationship analysis: {e}", exc_info=True)
                st.error(f"An error occurred during relationship analysis: {e}")


    # Network Analysis Tab
    with analysis_tabs[2]:
        st.markdown("### Network Analysis")

        if not current_graph:
            st.warning("Graph not available. Please process or load a book first.")
        elif current_graph.number_of_nodes() == 0:
             st.warning("Graph is empty, cannot perform network analysis.")
        else:
            G = current_graph
            num_nodes = G.number_of_nodes()
            num_edges = G.number_of_edges()

            st.markdown(f"Analyzing graph with {num_nodes} nodes and {num_edges} edges.")

            try:
                # Basic Statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Basic Properties")
                    st.metric("Nodes", num_nodes)
                    st.metric("Edges", num_edges)
                    if num_nodes > 1:
                        st.metric("Density", f"{nx.density(G):.4f}")
                    else:
                         st.metric("Density", "N/A (<=1 node)")

                    # Components (handle directed/undirected)
                    if G.is_directed():
                         if num_nodes > 0:
                             num_wcc = nx.number_weakly_connected_components(G)
                             st.metric("Weakly Connected Components", num_wcc)
                             # Only calculate SCC if graph is weakly connected and potentially has cycles
                             if num_wcc == 1:
                                 try:
                                     num_scc = nx.number_strongly_connected_components(G)
                                     st.metric("Strongly Connected Components", num_scc)
                                 except Exception as e_scc:
                                     logger.warning(f"Could not calculate SCC: {e_scc}")
                                     st.metric("Strongly Connected Components", "Error")
                             else:
                                 st.metric("Strongly Connected Components", "N/A (>1 WCC)")
                         else:
                            st.metric("Weakly Connected Components", 0)
                            st.metric("Strongly Connected Components", 0)
                    else: # Undirected
                        if num_nodes > 0:
                            st.metric("Connected Components", nx.number_connected_components(G))
                        else:
                            st.metric("Connected Components", 0)

                # Centrality Measures
                with col2:
                    st.markdown("#### Centrality (Top 5 Nodes)")
                    limit = 5 # Top N nodes to show

                    # Degree Centrality (Fast)
                    st.markdown("**Degree Centrality:**")
                    if num_nodes > 0:
                        with st.spinner("Calculating Degree Centrality..."):
                            degree_centrality = nx.degree_centrality(G)
                            top_degree_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:limit]

                        if top_degree_nodes:
                            degree_data = [{"Node": G.nodes[node_id].get('name', node_id), "Centrality": f"{centrality:.4f}"}
                                           for node_id, centrality in top_degree_nodes]
                            st.dataframe(pd.DataFrame(degree_data), hide_index=True)
                        else:
                            st.info("No nodes for degree centrality.")
                    else:
                        st.info("Graph has no nodes.")


                    # Betweenness Centrality (Potentially Slow)
                    # Add a threshold or make it optional
                    max_nodes_for_betweenness = 500
                    st.markdown("**Betweenness Centrality:**")
                    if num_nodes == 0:
                         st.info("Graph has no nodes.")
                    elif num_nodes <= max_nodes_for_betweenness:
                        try:
                            with st.spinner(f"Calculating Betweenness Centrality (nodes={num_nodes})..."):
                                # Use approximation for larger graphs if needed (k parameter)
                                k_val = min(100, num_nodes) if num_nodes > 100 else None # Sample k nodes
                                betweenness_centrality = nx.betweenness_centrality(G, k=k_val, normalized=True, seed=42)
                                top_betweenness_nodes = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:limit]

                            if top_betweenness_nodes:
                                 betweenness_data = [{"Node": G.nodes[node_id].get('name', node_id), "Centrality": f"{centrality:.4f}"}
                                                     for node_id, centrality in top_betweenness_nodes]
                                 st.dataframe(pd.DataFrame(betweenness_data), hide_index=True)
                            else:
                                st.info("No nodes ranked for betweenness centrality.")

                        except Exception as e:
                             logger.warning(f"Betweenness centrality calculation failed: {e}")
                             st.warning(f"Could not calculate Betweenness Centrality: {e}")
                    else:
                        st.info(f"Betweenness Centrality calculation skipped (graph > {max_nodes_for_betweenness} nodes).")


                # Advanced Network Analysis (Optional)
                with st.expander("Advanced Analysis (May be slow)", expanded=False):
                    if num_nodes == 0:
                        st.info("Graph is empty.")
                    elif st.button("Calculate Community Structure"):
                        try:
                            with st.spinner("Detecting communities using Louvain method..."):
                                # Use Louvain for undirected graphs or convert directed
                                if G.is_directed():
                                    # Community detection on directed graphs is complex.
                                    # Convert to undirected or use algorithms supporting directedness if available.
                                    # For simplicity, convert to undirected for Louvain.
                                    H = G.to_undirected(as_view=True) # Use view for efficiency
                                    logger.info("Working on undirected view of the graph for community detection.")
                                else:
                                    H = G

                                # Check if graph has edges before running community detection
                                if H.number_of_edges() == 0:
                                    st.info("No edges in the graph to detect communities.")
                                else:
                                    # Using python-louvain (community package) if installed
                                    # Or networkx's implementation
                                    try:
                                         # Attempt NetworkX greedy modularity (simpler, built-in)
                                         communities_generator = nx.community.greedy_modularity_communities(H)
                                         communities = [frozenset(c) for c in communities_generator] # Convert to list of sets
                                    except ImportError:
                                         st.error("Community detection requires additional libraries (like 'python-louvain'). Please install.")
                                         communities = None
                                    except Exception as e_comm:
                                         logger.error(f"NetworkX community detection failed: {e_comm}", exc_info=True)
                                         st.error(f"Community detection failed: {e_comm}")
                                         communities = None


                                    if communities:
                                        num_communities = len(communities)
                                        st.success(f"Detected {num_communities} communities.")

                                        # Display info about top communities by size
                                        communities.sort(key=len, reverse=True)
                                        st.markdown("**Largest Communities (Top 5):**")
                                        comm_data = []
                                        for i, comm_set in enumerate(communities[:5]):
                                            comm_size = len(comm_set)
                                            # Show sample nodes
                                            sample_nodes = [G.nodes[node].get('name', node) for node in list(comm_set)[:5]]
                                            comm_data.append({
                                                "Community": i + 1,
                                                "Size": comm_size,
                                                "Sample Nodes": ", ".join(sample_nodes) + ("..." if len(comm_set) > 5 else "")
                                            })
                                        st.dataframe(pd.DataFrame(comm_data), hide_index=True)
                                    elif communities is not None: # Check if it ran but found none
                                        st.info("No distinct communities were detected.")

                        except Exception as e:
                            logger.error(f"Error calculating communities: {e}", exc_info=True)
                            st.error(f"An error occurred during community detection: {e}")

            except Exception as e:
                logger.error(f"Error during network analysis: {e}", exc_info=True)
                st.error(f"An error occurred during network analysis: {e}")


    # Text View Tab
    with analysis_tabs[3]:
        st.markdown("### Text Representation")

        if entities_map or relationships_map:
             try:
                with st.spinner("Generating text tree view..."):
                    # Ensure maps are not None before passing
                    entities = entities_map if entities_map else {}
                    relationships = relationships_map if relationships_map else {}
                    tree_text = create_tree_display(entities, relationships)
                st.code(tree_text, language=None) # Use st.code for better formatting of text blocks
             except Exception as e:
                logger.error(f"Error generating text view: {e}", exc_info=True)
                st.error(f"Failed to generate text view: {e}")
        else:
            st.warning("No entities or relationships available for text view.")

# ... (settings_tab remains the same) ...
def settings_tab():
    """Settings Tab Content"""
    st.markdown("## Settings")

    # Database Connection Settings
    st.markdown("### Database Connection (Optional)")
    st.info("Configure ArangoDB connection details if you want to upload graphs.")

    # Use placeholders for sensitive info if available
    db_url_default = os.environ.get('DATABASE_HOST', 'http://localhost:8529')
    db_user_default = os.environ.get('DATABASE_USERNAME', 'root')
    # Do not default password in UI

    # Use session state to store temp DB settings for testing/uploading
    if 'db_url' not in st.session_state:
        st.session_state.db_url = db_url_default
    if 'db_username' not in st.session_state:
        st.session_state.db_username = db_user_default
    if 'db_password' not in st.session_state:
        st.session_state.db_password = ""

    st.session_state.db_url = st.text_input("Database URL", value=st.session_state.db_url)
    st.session_state.db_username = st.text_input("Database Username", value=st.session_state.db_username)
    st.session_state.db_password = st.text_input("Database Password", value=st.session_state.db_password, type="password")

    if st.button("Test Connection"):
        # Temporarily set env vars for the test function if db_service relies on them
        # A better approach is to pass credentials directly to is_db_connected
        # Assuming is_db_connected can accept credentials:
        # connected = is_db_connected(host=st.session_state.db_url, ...)
        # If not, revert to env var method:
        original_env = os.environ.copy()
        os.environ['DATABASE_HOST'] = st.session_state.db_url
        os.environ['DATABASE_USERNAME'] = st.session_state.db_username
        os.environ['DATABASE_PASSWORD'] = st.session_state.db_password

        with st.spinner("Testing database connection..."):
            try:
                connected = is_db_connected() # Assumes this uses the env vars just set
            except Exception as e:
                logger.error(f"DB connection test failed: {e}", exc_info=True)
                connected = False
                st.error(f"Connection test error: {e}")

        # Restore original env vars
        os.environ.clear()
        os.environ.update(original_env)

        if connected:
            st.success("Successfully connected to database!")
        elif 'connected' in locals() and not connected: # Only show error if test ran and failed
            st.error("Failed to connect to database. Check URL, username, and password.")

    # ArangoDB Integration
    st.markdown("### ArangoDB Graph Upload")

    if st.session_state.current_book_metadata and st.session_state.current_graph:
        book_name = st.session_state.current_book_metadata.book_name
        if st.button(f"Upload '{book_name}' Graph to ArangoDB"):
            # Set env vars before calling if needed by create_arango_graph
            original_env = os.environ.copy()
            os.environ['DATABASE_HOST'] = st.session_state.db_url
            os.environ['DATABASE_USERNAME'] = st.session_state.db_username
            os.environ['DATABASE_PASSWORD'] = st.session_state.db_password

            with st.spinner(f"Uploading graph for '{book_name}' to ArangoDB..."):
                try:
                    # Pass graph object and name
                    db_graph = create_arango_graph(st.session_state.current_graph, book_name)
                    if db_graph:
                        st.success(f"Successfully uploaded graph '{db_graph.name}' to ArangoDB!")
                    else:
                        # Check logs or db_service for specific error reason
                        st.error("Failed to upload graph to ArangoDB. The service returned None. Check connection and logs.")
                except Exception as e:
                    logger.error(f"Error uploading to ArangoDB: {e}", exc_info=True)
                    st.error(f"Error uploading graph: {e}")
                finally:
                    # Restore original env vars
                    os.environ.clear()
                    os.environ.update(original_env)
    else:
        st.info("Load a book with a graph to enable ArangoDB upload.")

    # Cache Management
    st.markdown("### Local Cache Management")
    cache_dir = Path("data") # Define cache directory

    # List cached books
    cached_books = get_cached_book_list()
    if cached_books and cached_books[0] != "No cached books found":
        st.write("Books currently in cache:")
        # Use a unique key for the selectbox here
        book_to_delete = st.selectbox("Select a book to delete from cache:", cached_books, key="delete_selectbox")

        if st.button("Delete Selected Book from Cache", type="secondary"):
            if book_to_delete:
                 with st.spinner(f"Deleting '{book_to_delete}' from cache..."):
                    try:
                        success = delete_cached_book(book_to_delete) # Assumes this function handles file deletion
                    except Exception as e:
                        logger.error(f"Error during cache deletion call for {book_to_delete}: {e}", exc_info=True)
                        success = False
                        st.error(f"Error occurred while trying to delete: {e}")

                 if success:
                    st.success(f"Successfully deleted '{book_to_delete}' from cache.")
                    # If the deleted book was the current one, clear state
                    if (st.session_state.current_book_metadata and
                        st.session_state.current_book_metadata.book_name == book_to_delete):
                        st.session_state.current_book_metadata = None
                        st.session_state.current_graph = None
                        st.session_state.current_book_name = ""
                        st.warning("The currently loaded book was deleted.")
                    # Clear potentially stale cached list selection state
                    if 'selected_cached_book' in st.session_state:
                         del st.session_state['selected_cached_book']
                    st.rerun() # Rerun to update the listbox and state
                 elif 'success' in locals() and not success: # Only show error if deletion attempted and failed
                    st.error(f"Failed to delete '{book_to_delete}'. Check logs or file permissions.")
            else:
                st.warning("Please select a book to delete.")
    else:
        st.info("The local cache is empty.")

    # Clear All Cache Button (use with caution)
    st.markdown("---")
    # Use a more descriptive key for the button
    if st.button("⚠️ Clear Entire Local Cache", key="clear_all_cache_button", type="primary"):
        # Add confirmation step
        if 'confirm_delete_cache' not in st.session_state:
            st.session_state.confirm_delete_cache = False

        st.session_state.confirm_delete_cache = True
        st.warning("This will delete all processed book data from the 'data' directory. Are you sure?")

    if st.session_state.get('confirm_delete_cache', False):
         # Show confirmation buttons only if primary button was clicked
         col_confirm, col_cancel = st.columns(2)
         with col_confirm:
             if st.button("Yes, Clear All Cache Now"):
                try:
                    with st.spinner("Clearing cache..."):
                        deleted_count = 0
                        errors_deleting = []
                        if cache_dir.exists() and cache_dir.is_dir():
                            import shutil
                            for item in cache_dir.iterdir():
                                try:
                                    if item.is_file(): # Delete loose files (e.g., .pkl)
                                        item.unlink()
                                        deleted_count += 1
                                    elif item.is_dir(): # Delete subdirectories
                                        shutil.rmtree(item)
                                        deleted_count += 1 # Count dir as one item
                                except Exception as item_e:
                                     errors_deleting.append(f"Could not delete {item.name}: {item_e}")
                        else:
                             st.info("'data' directory not found.")

                        # Reset session state if a book was loaded
                        st.session_state.current_book_metadata = None
                        st.session_state.current_graph = None
                        st.session_state.current_book_name = ""
                        if 'selected_cached_book' in st.session_state:
                            del st.session_state['selected_cached_book'] # Clear selection state too


                    if not errors_deleting:
                        st.success(f"Successfully cleared cache (removed approx. {deleted_count} items/folders).")
                    else:
                        st.warning(f"Cache clearing partially succeeded. Removed {deleted_count} items. Errors encountered:")
                        for err in errors_deleting:
                            st.error(err)

                    st.session_state.confirm_delete_cache = False # Reset confirmation flag
                    st.rerun() # Update UI
                except Exception as e:
                    logger.error(f"Failed to clear cache: {e}", exc_info=True)
                    st.error(f"Failed to clear cache: {e}")
                    st.session_state.confirm_delete_cache = False # Reset confirmation flag

         with col_cancel:
             if st.button("Cancel"):
                 st.session_state.confirm_delete_cache = False # Reset confirmation flag
                 st.rerun()

# Helper functions for the UI

def load_book(book_name):
    """Load a book from cache by name (Synchronous)"""
    logger.info(f"Attempting to load book: {book_name}")
    st.session_state.error_message = "" # Clear previous errors
    try:
        # select_cached_book should load the BookMetadata object
        book_metadata = select_cached_book(book_name)

        if not book_metadata:
            st.session_state.error_message = f"Error: Book '{book_name}' not found or failed to load from cache."
            logger.warning(f"Book '{book_name}' not found in cache or failed to load.")
            # Reset state
            st.session_state.current_book_metadata = None
            st.session_state.current_graph = None
            st.session_state.current_book_name = ""
            st.rerun() # Rerun to show the error and clear UI
            return # Stop execution here

        logger.info(f"Book metadata loaded for '{book_name}'. Creating graph...")
        # Create graph directly from the loaded book metadata
        # This might also take time
        graph = create_graph_from_book_metadata(book_metadata)

        if not isinstance(graph, nx.Graph): # Check if it's a valid graph object
             st.session_state.error_message = "Error: Failed to create graph from loaded book metadata. Check logs."
             logger.error(f"Failed to create graph for '{book_name}' from metadata. Result was not a NetworkX graph.")
             # Clear potentially partially loaded data
             st.session_state.current_book_metadata = None
             st.session_state.current_graph = None
             st.session_state.current_book_name = ""
             st.rerun() # Rerun to show the error
             return # Stop execution

        # Log if graph is empty but proceed
        if graph.number_of_nodes() == 0:
             logger.warning(f"Created an empty graph (0 nodes) for '{book_name}'.")
             # Decide if this should be an error or just a warning shown to user later

        # Update session state successfully
        st.session_state.current_book_metadata = book_metadata
        st.session_state.current_graph = graph
        st.session_state.current_book_name = book_name
        st.session_state.error_message = "" # Clear error on success

        logger.info(f"Successfully loaded book and created graph for: {book_name}")
        # Let the calling function handle the rerun via spinner exit

    except Exception as e:
        logger.error(f"Error loading book '{book_name}': {e}", exc_info=True)
        st.session_state.error_message = f"An unexpected error occurred loading '{book_name}': {e}"
        # Reset state in case of failure
        st.session_state.current_book_metadata = None
        st.session_state.current_graph = None
        st.session_state.current_book_name = ""
        st.rerun() # Rerun to show error


def process_uploaded_book(uploaded_file, book_name, status_callback=None):
    """Process an uploaded PDF book (Synchronous)"""
    if not uploaded_file:
        st.session_state.error_message = "Error: No file uploaded."
        # No rerun needed, error displayed in current run
        return

    if not book_name:
        st.session_state.error_message = "Error: Book name cannot be empty."
        # No rerun needed
        return

    logger.info(f"Starting processing for uploaded file: {uploaded_file.name} as '{book_name}'")

    # Define temp file path
    temp_dir = Path("./temp_uploads")
    try:
        temp_dir.mkdir(exist_ok=True) # Create dir if it doesn't exist
    except OSError as e:
        logger.error(f"Failed to create temp directory {temp_dir}: {e}")
        st.session_state.error_message = f"Error creating temporary directory: {e}"
        st.rerun()
        return

    # Sanitize book_name slightly for filename safety, or use UUID
    safe_suffix = "".join(c if c.isalnum() else "_" for c in book_name)
    safe_filename = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_suffix}.pdf"
    temp_file_path = temp_dir / safe_filename

    logger.info(f"Saving uploaded file temporarily to: {temp_file_path}")
    try:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        logger.error(f"Failed to write temporary file: {e}", exc_info=True)
        st.session_state.error_message = f"Error saving uploaded file: {e}"
        # No finally block needed here as state is set and we return
        st.rerun() # Rerun to show error
        return

    # Reset state for the new processing task
    st.session_state.current_book_metadata = None
    st.session_state.current_graph = None
    st.session_state.current_book_name = ""
    st.session_state.error_message = ""

    # Use the callback for status updates (will update spinner text)
    def update_progress(message):
        if status_callback:
            status_callback(message)

    graph = None
    book_meta = None
    processing_error = None
    start_time = time.time()

    try:
        # 1. Extract Text
        update_progress("Extracting text from PDF...")
        book_text = extract_text_from_pdf(str(temp_file_path)) # Pass path as string

        # Check if extraction failed
        if not book_text or (isinstance(book_text, str) and book_text.startswith("Error")):
            processing_error = f"Text extraction failed: {book_text}" if book_text else "Text extraction failed: Empty result."
            logger.error(processing_error)
            raise ValueError(processing_error) # Raise exception to go to finally block

        text_length = len(book_text)
        logger.info(f"Text extracted successfully. Length: {text_length}.")
        update_progress(f"Text extracted ({text_length:,} chars). Creating graph...")

        graph, book_meta = create_graph_from_text(book_text, status_callback=update_progress)
        
        # --- Add this logging ---
        logger.info(f"Returned book_meta type: {type(book_meta)}")
        if isinstance(book_meta, BookMetadata):
             logger.info(f"Book Meta has entities_map: {hasattr(book_meta, 'entities_map')}")
             entities_map_content = getattr(book_meta, 'entities_map', 'Attribute Missing')
             logger.info(f"Entities Map content (type: {type(entities_map_content)}, len: {len(entities_map_content) if isinstance(entities_map_content, dict) else 'N/A'}): {str(entities_map_content)[:500]}...") # Log first 500 chars
        
             logger.info(f"Book Meta has relationships_map: {hasattr(book_meta, 'relationships_map')}")
             relationships_map_content = getattr(book_meta, 'relationships_map', 'Attribute Missing')
             logger.info(f"Relationships Map content (type: {type(relationships_map_content)}, len: {len(relationships_map_content) if isinstance(relationships_map_content, dict) else 'N/A'}): {str(relationships_map_content)[:500]}...") # Log first 500 chars
        else:
             logger.warning(f"book_meta object returned from create_graph_from_text is not a BookMetadata instance (type: {type(book_meta)}).")
        # --- End of added logging ---

        # Check results
        if not isinstance(graph, nx.Graph) or not isinstance(book_meta, BookMetadata):
            processing_error = "Graph or metadata creation failed (invalid result type). Check logs."
            logger.error(f"{processing_error}. Graph type: {type(graph)}, Meta type: {type(book_meta)}")
            if not st.session_state.error_message: # Set error if not already set by internal function
                st.session_state.error_message = processing_error
            raise ValueError(processing_error)

        logger.info(f"Graph ({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges) and metadata created successfully for '{book_name}'.")

        # --- ADDED: Set processing_date ---
        book_meta.processing_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Also set original file name
        book_meta.file_name = uploaded_file.name

        update_progress("Graph created. Saving metadata...")

        # 3. Save Metadata (Cache)
        if not save_book_metadata(book_meta):
            # Log warning but continue - processing succeeded, caching failed
            logger.warning(f"Book processed but failed to save metadata for '{book_name}' to cache.")
            st.warning("Book processed successfully, but failed to save to local cache.") # Show user warning
        else:
            logger.info(f"Book metadata saved successfully for '{book_name}'.")
            update_progress("Book processed and saved to cache.")

        # 4. Update Session State (on success)
        st.session_state.current_book_metadata = book_meta
        st.session_state.current_graph = graph
        st.session_state.current_book_name = book_name
        st.session_state.error_message = "" # Clear any previous error

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"Successfully processed book '{book_name}' in {processing_time:.2f} seconds.")
        update_progress(f"Successfully processed book: {book_name}")
        # Success message will be shown after rerun

    except Exception as e:
        # Log the full error, show simpler message to user
        logger.error(f"Error processing book '{book_name}': {e}", exc_info=True)
        final_error_message = processing_error if processing_error else f"An processing error occurred: {e}"
        st.session_state.error_message = final_error_message
        # Reset potentially partially filled state
        st.session_state.current_book_metadata = None
        st.session_state.current_graph = None
        st.session_state.current_book_name = ""
        update_progress(f"Error: {final_error_message}") # Update status one last time

    finally:
        # Clean up the temporary file regardless of success or failure
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
                logger.info(f"Deleted temporary file: {temp_file_path}")
        except Exception as e_clean:
            logger.warning(f"Could not delete temporary file {temp_file_path}: {e_clean}")

        # Force a rerun to update the UI after the spinner context closes
        # This ensures messages (success/error) and state changes are reflected
        st.rerun()


# Run the app
if __name__ == "__main__":
    # Basic check for essential directories
    Path("./data").mkdir(exist_ok=True)
    Path("./temp_uploads").mkdir(exist_ok=True)
    main()