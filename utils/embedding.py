import logging
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
model = None

def load_embedding_model(model_name='intfloat/e5-small-v2'):
    """
    Load the embedding model globally.
    
    Args:
        model_name: The name or path of the model to load
        
    Returns:
        bool: True if successful, False otherwise
    """
    global model
    try:
        model = SentenceTransformer(model_name)
        logging.info(f"Loaded embedding model: {model_name}")
        return True
    except Exception as e:
        logging.error(f"Error loading embedding model: {e}")
        return False

def generate_embedding(text):
    """
    Generate an embedding vector for a given text.
    
    Args:
        text: The text to embed
        
    Returns:
        list: The embedding vector
    """
    global model
    if model is None:
        load_embedding_model()
    
    if model is None:
        logging.error("Embedding model not available")
        return None
    
    try:
        return model.encode(text, normalize_embeddings=True).tolist()
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

def calculate_similarity(embed1, embed2):
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embed1: First embedding vector
        embed2: Second embedding vector
        
    Returns:
        float: Cosine similarity score
    """
    import numpy as np
    
    if not embed1 or not embed2:
        return 0.0
    
    try:
        # Convert to numpy arrays if they're lists
        if isinstance(embed1, list):
            embed1 = np.array(embed1)
        if isinstance(embed2, list):
            embed2 = np.array(embed2)
            
        # Normalize vectors
        embed1_norm = embed1 / np.linalg.norm(embed1)
        embed2_norm = embed2 / np.linalg.norm(embed2)
        
        # Calculate cosine similarity
        return float(np.dot(embed1_norm, embed2_norm))
    except Exception as e:
        logging.error(f"Error calculating similarity: {e}")
        return 0.0