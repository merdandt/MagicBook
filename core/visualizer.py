import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import logging
from typing import Dict, List, Any, Optional, Tuple

def visualize_networkx_graph(G, book_name, figsize=(15, 10), min_degree_for_labels=3):
    """
    Create a static NetworkX visualization with matplotlib.
    
    Args:
        G: NetworkX graph to visualize
        book_name: Title for the visualization
        figsize: Figure size as (width, height)
        min_degree_for_labels: Minimum node degree to display labels
        
    Returns:
        tuple: (fig, ax) matplotlib figure and axis objects
    """
    # Define colors for node types
    node_colors = {
        'CHARACTER': '#3357FF',  # Blue
        'LOCATION': '#33FFF5',   # Cyan
        'EVENT': '#A64DFF',      # Purple
        'ITEM': '#F5FF33',       # Yellow
        'ORGANIZATION': '#FF5733', # Orange
        'CONCEPT': '#FF33A8',    # Pink
        'TIME_PERIOD': '#8C8C8C', # Gray
        'CHAPTER': '#33FF57'     # Green
    }
    
    # Create layout and figure
    pos = nx.spring_layout(G, iterations=15, seed=1721) 
    fig, ax = plt.subplots(figsize=figsize)
    
    # Group nodes by type
    node_groups = {}
    for node in G.nodes():
        node_type = G.nodes[node].get('entity_type', 'unknown')
        if node_type not in node_groups:
            node_groups[node_type] = []
        node_groups[node_type].append(node)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.15, ax=ax)
    
    # Draw nodes by type
    for node_type, nodes in node_groups.items():
        color = node_colors.get(node_type, '#CCCCCC')  # Default gray for unknown types
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes,
            node_color=color,
            node_size=40,
            alpha=0.8,
            ax=ax
        )
    
    # Create labels for high-degree nodes
    high_degree_nodes = [n for n, d in G.degree() if d > min_degree_for_labels]
    
    # Create label dictionary using name or title based on node type
    labels = {}
    for node in high_degree_nodes:
        node_type = G.nodes[node].get('entity_type', '')
        if node_type == 'CHAPTER':
            labels[node] = G.nodes[node].get('title', str(node))
        else:
            labels[node] = G.nodes[node].get('name', str(node))
    
    # Draw labels if there are any high-degree nodes
    if labels:
        nx.draw_networkx_labels(
            G, pos,
            labels,
            font_size=6,
            font_color='black',
            ax=ax
        )
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=color, label=f"{node_type} ({len(node_groups.get(node_type, []))})")
        for node_type, color in node_colors.items()
        if node_type in node_groups
    ]
    
    # Add legend, title, and formatting
    ax.legend(handles=legend_elements, loc='upper right')
    plt.axis('off')
    plt.title(book_name, fontsize=16)
    plt.tight_layout()
    
    return fig, ax

def create_plotly_graph(G, book_name):
    """
    Create an interactive Plotly graph from NetworkX graph.
    
    Args:
        G: NetworkX graph to visualize
        book_name: Title for the visualization
        
    Returns:
        plotly.graph_objects.Figure: Interactive Plotly figure
    """
    # Define colors for node types
    node_colors = {
        'CHARACTER': '#3357FF',  # Blue
        'LOCATION': '#33FFF5',   # Cyan
        'EVENT': '#A64DFF',      # Purple
        'ITEM': '#F5FF33',       # Yellow
        'ORGANIZATION': '#FF5733', # Orange
        'CONCEPT': '#FF33A8',    # Pink
        'TIME_PERIOD': '#8C8C8C', # Gray
        'CHAPTER': '#33FF57'     # Green
    }
    
    # Group nodes by type for color assignments
    node_color_map = {}
    node_type_counts = {}
    
    for node in G.nodes():
        node_type = G.nodes[node].get('entity_type', 'unknown')
        color = node_colors.get(node_type, '#CCCCCC')  # Default gray for unknown
        node_color_map[node] = color
        
        # Count nodes by type
        if node_type not in node_type_counts:
            node_type_counts[node_type] = 0
        node_type_counts[node_type] += 1
    
    # Create positions for nodes
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge traces
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)
    
    # Create node traces by entity type
    node_traces = []
    
    for node_type, color in node_colors.items():
        if node_type not in node_type_counts:
            continue
            
        # Collect nodes of this type
        nodes = [node for node in G.nodes() if G.nodes[node].get('entity_type') == node_type]
        
        # Skip if no nodes of this type
        if not nodes:
            continue
            
        # Create trace for this node type
        trace = go.Scatter(
            x=[pos[node][0] for node in nodes],
            y=[pos[node][1] for node in nodes],
            mode='markers',
            name=f"{node_type} ({node_type_counts[node_type]})",
            marker=dict(
                size=10,
                color=color,
                line=dict(width=1, color='#333')
            ),
            text=[G.nodes[node].get('name', str(node)) for node in nodes],
            hoverinfo='text',
            hovertemplate='%{text}<extra></extra>'
        )
        
        node_traces.append(trace)
    
    # Create the figure
    layout = go.Layout(
        title=book_name,
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=800,
        legend=dict(
            font=dict(size=10),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Create figure with all traces
    fig = go.Figure(data=[edge_trace] + node_traces, layout=layout)
    
    return fig

def create_tree_display(entities, relationships):
    """
    Creates a hierarchical tree display of entities and relationships for a book.
    
    Args:
        entities: Dictionary of entity data
        relationships: Dictionary of relationship data
        
    Returns:
        str: Formatted tree representation
    """
    if not entities or not relationships:
        return "No entities or relationships to display"
    
    tree_text = []
    
    # ENTITIES TREE
    tree_text.append("ENTITIES")
    tree_text.append("========")
    
    # Sort entity types for consistent display
    entity_types = sorted(list(entities.keys()))
    for entity_type in entity_types:
        entities_of_type = entities[entity_type]
        count = len(entities_of_type)
        tree_text.append(f"├── {entity_type} ({count})")
        
        # Add each entity under this type
        for i, entity in enumerate(entities_of_type):
            is_last = i == len(entities_of_type) - 1
            prefix = "└── " if is_last else "├── "
            name = entity.get("name", "Unnamed")
            key = entity.get("_key", "")
            tree_text.append(f"│   {prefix}{name} [{key}]")
    
    # Add spacing
    tree_text.append("")
    
    # RELATIONSHIPS TREE
    tree_text.append("RELATIONSHIPS")
    tree_text.append("=============")
    
    # Sort relationship types
    rel_types = sorted(list(relationships.keys()))
    for rel_type in rel_types:
        rels_of_type = relationships[rel_type]
        count = len(rels_of_type)
        tree_text.append(f"├── {rel_type} ({count})")
        
        # Process each relationship based on its structure
        for i, rel in enumerate(rels_of_type):
            is_last = i == len(rels_of_type) - 1
            prefix = "└── " if is_last else "├── "
            
            # Different relationship types have different structures
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
        # Generic fallback for other relationship types
        keys = list(rel.keys())[:2]  # Get first two keys
        return f"{keys[0]}: {rel[keys[0]]}, {keys[1]}: {rel[keys[1]]}"