from matplotlib import pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches



def visualize_graph_network(G_nx, book_name, output_file=None, figsize=(15, 9), min_degree_for_labels=10):
    """
    Visualize a NetworkX graph with nodes colored by type based on prefix.

    Parameters:
    -----------
    G_nx : networkx.Graph
        The graph to visualize, with node data attributes including 'type', 'name', and 'title'
    book_name : str
        Title for the graph visualization
    output_file : str, optional
        Path to save the visualization
    figsize : tuple, optional
        Figure size as (width, height)
    min_degree_for_labels : int, optional
        Minimum node degree required to show labels
    """
    # Create layout
    pos = nx.spring_layout(G_nx, iterations=15, seed=1721)
    fig, ax = plt.subplots(figsize=figsize)

    # Define colors for node types
    node_colors = {
        'CHARACTER': '#3357FF',     # Blue
        'LOCATION': '#33FFF5',      # Cyan
        'EVENT': '#A64DFF',         # Purple
        'ITEM': '#F5FF33',          # Yellow
        'ORGANIZATION': '#FF5733',  # Orange
        'CONCEPT': '#FF33A8',       # Pink
        'TIME_PERIOD': '#8C8C8C',   # Gray
        'CHAPTER': '#33FF57'        # Green
    }

    # Group nodes by type
    node_groups = {}
    for node in G_nx.nodes():
        node_type = G_nx.nodes[node].get('type', 'unknown')
        if node_type not in node_groups:
            node_groups[node_type] = []
        node_groups[node_type].append(node)

    # Draw edges
    nx.draw_networkx_edges(G_nx, pos, alpha=0.2, width=0.15, ax=ax)

    # Draw nodes by type
    for node_type, nodes in node_groups.items():
        color = node_colors.get(node_type, '#CCCCCC')  # Default gray for unknown types
        nx.draw_networkx_nodes(
            G_nx, pos,
            nodelist=nodes,
            node_color=color,
            node_size=40,
            alpha=0.8,
            ax=ax
        )

    # Create labels for high-degree nodes
    high_degree_nodes = [n for n, d in G_nx.degree() if d > min_degree_for_labels]

    # Create label dictionary using name or title based on node type
    labels = {}
    for node in high_degree_nodes:
        node_type = G_nx.nodes[node].get('type', '')
        if node_type == 'CHAPTER':
            labels[node] = G_nx.nodes[node].get('title', str(node))
        else:
            labels[node] = G_nx.nodes[node].get('name', str(node))

    # Draw labels if there are any high-degree nodes
    if labels:
        nx.draw_networkx_labels(
            G_nx, pos,
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

    # Save if output file specified
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')

    return fig, ax

# # Create visualization
# fig, ax = visualize_graph_network(G_nx, "The Lord of the Rings", "lotr_network.png")
# plt.show()