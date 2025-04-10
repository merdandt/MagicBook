import os
import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

from model.book_metadata import BookMetadata
from utils.file_utils import save_json, load_json

# Global variable to hold all BookMetadata instances
BOOK_METADATA_COLLECTION = []

def load_cached_books():
    """
    Load metadata of all cached books from the data directory
    
    Returns:
        list: List of BookMetadata objects
    """
    global BOOK_METADATA_COLLECTION
    
    # If collection is already populated, return it
    if BOOK_METADATA_COLLECTION:
        return BOOK_METADATA_COLLECTION
    
    # Ensure data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        logging.info(f"Created data directory at {data_dir.absolute()}")
        return []
    
    # Find all book directories
    book_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    loaded_books = []
    
    for book_dir in book_dirs:
        metadata_file = book_dir / "metadata.json"
        entities_file = book_dir / "entities.json"
        relationships_file = book_dir / "relationships.json"
        
        if not metadata_file.exists():
            continue
            
        try:
            metadata_dict = load_json(metadata_file)
            if not metadata_dict:
                continue
                
            book = BookMetadata(
                book_name=metadata_dict.get("book_name", ""),
                author=metadata_dict.get("author", ""),
                pages_count=metadata_dict.get("pages_count", ""),
                time_to_process=metadata_dict.get("time_to_process", ""),
                summary=metadata_dict.get("summary", "")
            )
            
            # Load entities and relationships if they exist
            if entities_file.exists():
                book.entities_map = load_json(entities_file)
                
            if relationships_file.exists():
                book.relationships_map = load_json(relationships_file)
                
            loaded_books.append(book)
            logging.info(f"Loaded book: {book.book_name}")
            
        except Exception as e:
            logging.error(f"Error loading book metadata from {metadata_file}: {e}")
    
    BOOK_METADATA_COLLECTION = loaded_books
    return BOOK_METADATA_COLLECTION

def select_cached_book(book_name):
    """
    Select a cached book by name from the collection
    
    Args:
        book_name: Name of the book to select
        
    Returns:
        BookMetadata: The selected book metadata or None if not found
    """
    books = load_cached_books()
    for book in books:
        if book.book_name == book_name:
            return book
    
    logging.error(f"Book '{book_name}' not found in cached collection")
    return None

def get_cached_book_list():
    """
    Get list of cached book names for dropdown
    
    Returns:
        list: List of book names
    """
    books = load_cached_books()
    return [book.book_name for book in books] if books else ["No cached books found"]

def save_book_metadata(book_metadata):
    """
    Save book metadata to cache directory
    
    Args:
        book_metadata: BookMetadata object to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not book_metadata or not book_metadata.book_name:
        logging.error("Cannot save book: Invalid book metadata")
        return False
    
    # Create book directory
    book_name_safe = book_metadata.book_name.replace(" ", "_").lower()
    book_dir = Path("data") / book_name_safe
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    metadata_dict = {
        "book_name": book_metadata.book_name,
        "author": book_metadata.author,
        "pages_count": book_metadata.pages_count,
        "time_to_process": book_metadata.time_to_process,
        "summary": book_metadata.summary
    }
    
    metadata_saved = save_json(metadata_dict, book_dir / "metadata.json")
    
    # Save entities and relationships if they exist
    entities_saved = True
    relationships_saved = True
    
    if book_metadata.entities_map:
        entities_saved = save_json(book_metadata.entities_map, book_dir / "entities.json")
        
    if book_metadata.relationships_map:
        relationships_saved = save_json(book_metadata.relationships_map, book_dir / "relationships.json")
    
    # Update global collection if not already present
    global BOOK_METADATA_COLLECTION
    book_exists = False
    
    for i, book in enumerate(BOOK_METADATA_COLLECTION):
        if book.book_name == book_metadata.book_name:
            BOOK_METADATA_COLLECTION[i] = book_metadata
            book_exists = True
            break
            
    if not book_exists:
        BOOK_METADATA_COLLECTION.append(book_metadata)
    
    return metadata_saved and entities_saved and relationships_saved

def download_repo_contents(api_url, local_dir='.', metadata_list=None):
    """
    Recursively downloads JSON and TXT files from a GitHub repo via its API,
    preserving the repository's folder structure locally.
    
    For each folder:
    - Temporarily stores JSON files (for entities and relationships).
    - When a file named 'book.txt' is found, parses it into a BookMetadata
      and assigns any previously stored JSON data.
    - If additional JSON files are found after 'book.txt', updates the object.
    
    Args:
        api_url (str): The GitHub API URL for the repository or folder.
        local_dir (str): The local directory where files will be saved.
        metadata_list (list): A list to store BookMetadata objects.
        
    Returns:
        metadata_list (list): The updated list of BookMetadata objects.
    """
    if metadata_list is None:
        metadata_list = []
        
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        items = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching {api_url}: {e}")
        return metadata_list
        
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
        
    # Temporary storage for JSON content in this folder
    temp_entities = None
    temp_relationships = None
    current_book = None
    
    for item in items:
        if item['type'] == 'file' and (item['name'].endswith('.json') or item['name'].endswith('.txt')):
            file_url = item.get('download_url')
            if not file_url:
                logging.warning(f"Missing download URL for {item['name']}")
                continue
                
            try:
                file_response = requests.get(file_url)
                file_response.raise_for_status()
            except requests.RequestException as e:
                logging.error(f"Error downloading {item['name']}: {e}")
                continue
                
            file_path = os.path.join(local_dir, item['name'])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_response.text)
                
            logging.info(f"Downloaded {item['name']} to {local_dir}")
            
            if item['name'].lower() == 'book.txt':
                # Create BookMetadata from book.txt and assign any JSON data
                try:
                    current_book = BookMetadata.from_txt(file_response.text)
                    current_book.entities_map = temp_entities
                    current_book.relationships_map = temp_relationships
                except Exception as e:
                    logging.error(f"Error parsing {item['name']}: {e}")
            elif item['name'].endswith('.json'):
                # Load JSON data from the file
                json_data = load_json(file_path)
                if json_data is None:
                    continue
                    
                if 'entities' in item['name'].lower():
                    temp_entities = json_data
                    if current_book is not None:
                        current_book.entities_map = json_data
                elif 'relationship' in item['name'].lower():
                    temp_relationships = json_data
                    if current_book is not None:
                        current_book.relationships_map = json_data
        elif item['type'] == 'dir':
            new_local_dir = os.path.join(local_dir, item['name'])
            download_repo_contents(item['url'], new_local_dir, metadata_list)
            
    # If a BookMetadata object was created in this folder, add it to the list
    if current_book:
        metadata_list.append(current_book)
        
        # Also save to local cache
        save_book_metadata(current_book)
        
    return metadata_list

def delete_cached_book(book_name):
    """
    Delete a cached book by name
    
    Args:
        book_name: Name of the book to delete
        
    Returns:
        bool: True if deleted, False otherwise
    """
    if not book_name:
        logging.error("Cannot delete book: No book name provided")
        return False
    
    # Find the book in the collection
    global BOOK_METADATA_COLLECTION
    book_to_delete = None
    
    for book in BOOK_METADATA_COLLECTION:
        if book.book_name == book_name:
            book_to_delete = book
            break
            
    if not book_to_delete:
        logging.error(f"Book '{book_name}' not found in cached collection")
        return False
    
    # Remove from collection
    BOOK_METADATA_COLLECTION.remove(book_to_delete)
    
    # Delete directory
    book_name_safe = book_name.replace(" ", "_").lower()
    book_dir = Path("data") / book_name_safe
    
    if not book_dir.exists():
        logging.warning(f"Book directory not found: {book_dir}")
        return True  # Book removed from collection successfully
    
    try:
        # Delete all files in directory
        for file in book_dir.iterdir():
            file.unlink()
        
        # Delete directory
        book_dir.rmdir()
        logging.info(f"Deleted book directory: {book_dir}")
        return True
    except Exception as e:
        logging.error(f"Error deleting book directory: {e}")
        return False