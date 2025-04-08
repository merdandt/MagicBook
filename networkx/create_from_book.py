import json
import time
from extractor.ensure_consistency import ensure_consistency
from extractor.entity_extractor import AsyncEntityRelationshipExtractor
from extractor.entity_relationships_schema import EntityType, RelationshipType
from extractor.text_extractor import extract_text_from_pdf
from networkx.create_functions import create_graph_with_embeddings
from prompts.entity_discover_prompt import ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT, ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT
from utils.json_functions import clean_json_string


async def create_graph_from_book(pdf_file):
    start = time.time()

    # Extract text from the PDF.
    try:
        book_text = extract_text_from_pdf(pdf_file)
    except Exception as e:
        print(f"Error extracting text from PDF '{pdf_file}': {e}")
        return None

    # Prepare the messages to be sent to the language model.
    try:
        messages = [
            {"role": "system", "content": ENTITY_RELATIONSHIPS_DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": ENTITY_RELATIONSHIPS_DISCOVERY_USER_PROMPT.format(book_text=book_text)}
        ]
    except Exception as e:
        print(f"Error preparing messages: {e}")
        return None

    # Invoke the language model.
    try:
        response = BOOK_LLM.invoke(messages)
    except Exception as e:
        print(f"Error invoking book_llm: {e}")
        return None

    # Clean and parse the returned JSON.
    try:
        cleaned_json = clean_json_string(response.content)
        print('Cleaned JSON:')
        print(cleaned_json)
    except Exception as e:
        print(f"Error cleaning JSON string: {e}")
        return None

    try:
        book_entities_json = json.loads(cleaned_json)
        print('Entities JSON:')
        print(book_entities_json)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

    # Ensure consistency in the entities and relationships.
    try:
        ensured_entities, ensured_relationships = ensure_consistency(
            book_entities_json['Entities'],
            book_entities_json['Relationships'],
            reference_mappings,
            threshold=2
        )
    except Exception as e:
        print(f"Error ensuring consistency: {e}")
        return None

    # Initialize the asynchronous entity-relationship extractor.
    try:
        extractor = AsyncEntityRelationshipExtractor(
            chat_model=BOOK_LLM,
            entity_types=[EntityType[e] for e in ensured_entities],
            relationship_types=[RelationshipType[r] for r in ensured_relationships],
            entity_prompts_map=entity_prompts_map,
            relationship_prompts_map=relationships_prompts_map,
            reference_mappings=reference_mappings,
            book_text=book_text
        )
    except Exception as e:
        print(f"Error initializing AsyncEntityRelationshipExtractor: {e}")
        return None

    # Define an async function to perform extraction.
    async def test_extraction():
        try:
            filled_entities, filled_relationships = await extractor.extract_all_async()
            return filled_entities, filled_relationships
        except Exception as e:
            print(f"Error during asynchronous extraction: {e}")
            return None, None

    # Await the asynchronous extraction.
    try:
        filled_entities, filled_relationships = await test_extraction()
        if filled_entities is None or filled_relationships is None:
            print("Error: Extraction returned None for entities or relationships.")
            return None
    except Exception as e:
        print(f"Error awaiting extraction: {e}")
        return None

    # Create the graph with embeddings from the extracted data.
    try:
        G_nx = create_graph_with_embeddings(filled_entities, filled_relationships)
    except Exception as e:
        print(f"Error creating graph with embeddings: {e}")
        return None

    end = time.time()
    print(f"Time taken to process book: {end - start} seconds")
    return G_nx, filled_entities, filled_relationships
