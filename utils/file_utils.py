import os
import json
import logging
import PyPDF2
import tempfile
import requests
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file with no length constraints.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text from PDF
    """
    logging.debug(f"Starting PDF text extraction from file: {pdf_path}")
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        logging.debug(f"Opened PDF file successfully. Total pages: {len(pdf_reader.pages)}")
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            # Log the first 100 characters from the page's text for debugging
            if page_text:
                logging.debug(f"Page {page_num+1} extracted text (first 100 chars): {page_text[:100]}...")
                text += page_text + "\n"
            else:
                logging.debug(f"No text found on page {page_num + 1}")
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logging.error(error_msg)
        return error_msg
    
    logging.debug(f"Completed PDF text extraction. Total extracted text length: {len(text)} characters")
    return text

def save_json(data, filepath):
    """Save data as JSON to a file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
        return False

def load_json(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {filepath}")
        return None
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        return None

def clean_json_string(json_data):
    """Clean and format JSON strings returned by the AI, and fix truncation issues"""
    import re
    
    # Remove markdown code block markers and optional language specifier
    json_data = re.sub(r'^```(?:json)?\s*', '', json_data, flags=re.IGNORECASE)
    json_data = re.sub(r'\s*```$', '', json_data)
    json_data = json_data.strip()
    
    if not json_data:
        return json_data
    
    # Determine if we're dealing with a JSON array or object
    first_char = json_data[0]
    if first_char == '[':
        open_char, close_char = '[', ']'
    elif first_char == '{':
        open_char, close_char = '{', '}'
    else:
        return json_data  # Not a valid JSON object/array
    
    # Use a counter to track the balance of the brackets
    count = 0
    last_complete_index = None
    
    for i, ch in enumerate(json_data):
        if ch == open_char:
            count += 1
        elif ch == close_char:
            count -= 1
            if count == 0:
                last_complete_index = i
    
    # If a balanced closing bracket is found, truncate the string there
    if last_complete_index is not None:
        json_data = json_data[:last_complete_index + 1]
    
    # Ensure that the JSON ends with the proper closing bracket
    if first_char == '[' and not json_data.endswith(']'):
        json_data += ']'
    elif first_char == '{' and not json_data.endswith('}'):
        json_data += '}'
    
    return json_data.strip()

def download_and_save_file(url, local_path=None):
    """Download a file from URL and save it to a local path or temporary file"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        if local_path:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return local_path
        else:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                return tmp.name
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return None

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir

def list_files_in_directory(directory, extension=None):
    """List all files in a directory, optionally filtered by extension"""
    directory = Path(directory)
    if not directory.exists():
        return []
    
    files = [f for f in directory.iterdir() if f.is_file()]
    if extension:
        files = [f for f in files if f.suffix.lower() == extension.lower()]
    
    return files