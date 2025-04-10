import os
import json
import logging
from typing import Dict, List, Any, Optional
import networkx as nx
import nx_arangodb as nxadb
from arango import ArangoClient

# Load database configuration from environment or use defaults
DB_URL = os.environ.get('DATABASE_HOST', 'http://localhost:8529')
DB_USERNAME = os.environ.get('DATABASE_USERNAME', 'root')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'openSesame')  # Change in production!
DB_NAME = os.environ.get('DATABASE_NAME', '_system')

def get_arango_client():
    """
    Get an ArangoDB client connection
    
    Returns:
        arango.ArangoClient: ArangoDB client
        
    Raises:
        Exception: If connection fails
    """
    try:
        client = ArangoClient(hosts=DB_URL)
        return client
    except Exception as e:
        logging.error(f"Error connecting to ArangoDB: {e}")
        raise

def get_database():
    """
    Get a database connection
    
    Returns:
        arango.database.StandardDatabase: Database connection
        
    Raises:
        Exception: If connection fails
    """
    try:
        client = get_arango_client()
        db = client.db(DB_NAME, username=DB_USERNAME, password=DB_PASSWORD, verify=False)
        return db
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def create_arango_graph(G_nx, book_name):
    """
    Create an ArangoDB graph from a NetworkX graph
    
    Args:
        G_nx: NetworkX graph
        book_name: Name of the book for the graph
        
    Returns:
        nx_arangodb.Graph: ArangoDB graph or None if failed
    """
    if not G_nx:
        logging.error("Cannot create ArangoDB graph: Invalid NetworkX graph")
        return None
    
    try:
        # Get database connection
        db = get_database()
        
        # Create a safe graph name
        graph_name = book_name.replace(" ", "_").capitalize()
        
        # Create the graph
        G_adb = nxadb.Graph(
            name=graph_name,
            db=db,
            incoming_graph_data=G_nx,
            write_batch_size=50000
        )
        
        logging.info(f"Created ArangoDB graph '{graph_name}' with {G_nx.number_of_nodes()} nodes and {G_nx.number_of_edges()} edges")
        return G_adb
    except Exception as e:
        logging.error(f"Error creating ArangoDB graph: {e}")
        return None

def delete_arango_graph(book_name):
    """
    Delete an ArangoDB graph
    
    Args:
        book_name: Name of the book/graph
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Get database connection
        db = get_database()
        
        # Create a safe graph name
        graph_name = book_name.replace(" ", "_").capitalize()
        
        # Check if graph exists
        if db.has_graph(graph_name):
            graph = db.graph(graph_name)
            graph.delete()
            logging.info(f"Deleted ArangoDB graph '{graph_name}'")
            return True
        else:
            logging.warning(f"Graph '{graph_name}' not found in database")
            return False
    except Exception as e:
        logging.error(f"Error deleting ArangoDB graph: {e}")
        return False

def list_arango_graphs():
    """
    List all ArangoDB graphs
    
    Returns:
        list: List of graph names
    """
    try:
        # Get database connection
        db = get_database()
        
        # List graphs
        graphs = db.graphs()
        return [graph['name'] for graph in graphs]
    except Exception as e:
        logging.error(f"Error listing ArangoDB graphs: {e}")
        return []

def get_arango_graph(book_name):
    """
    Get an ArangoDB graph by name
    
    Args:
        book_name: Name of the book/graph
        
    Returns:
        arango.graph.Graph: ArangoDB graph or None if not found
    """
    try:
        # Get database connection
        db = get_database()
        
        # Create a safe graph name
        graph_name = book_name.replace(" ", "_").capitalize()
        
        # Check if graph exists
        if db.has_graph(graph_name):
            return db.graph(graph_name)
        else:
            logging.warning(f"Graph '{graph_name}' not found in database")
            return None
    except Exception as e:
        logging.error(f"Error getting ArangoDB graph: {e}")
        return None

def query_graph(graph_name, query, bind_vars=None):
    """
    Run an AQL query on a graph
    
    Args:
        graph_name: Name of the graph
        query: AQL query string
        bind_vars: Binding variables for the query
        
    Returns:
        list: Query results
    """
    if bind_vars is None:
        bind_vars = {}
        
    try:
        # Get database connection
        db = get_database()
        
        # Create a safe graph name
        graph_name = graph_name.replace(" ", "_").capitalize()
        
        # Check if graph exists
        if not db.has_graph(graph_name):
            logging.warning(f"Graph '{graph_name}' not found in database")
            return []
        
        # Run query
        cursor = db.aql.execute(query, bind_vars=bind_vars)
        return [doc for doc in cursor]
    except Exception as e:
        logging.error(f"Error querying graph: {e}")
        return []

def is_db_connected():
    """
    Check if database is connected
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        db = get_database()
        return True
    except:
        return False