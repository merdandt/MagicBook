# Initialize embedding model
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('intfloat/e5-small-v2')  # Efficient and lightweight

# Function to generate embeddings
def generate_embedding(text):
    return model.encode(text, normalize_embeddings=True).tolist()