from concurrent.futures import ThreadPoolExecutor
import json
import logging
import time

from model.book_metadata import BookMetadata
from utils.file_utils import clean_json_string
from utils.simple_cache import load as cache_load, save as cache_save



class EntityRelationshipExtractor:
    """
    Builds a narrative graph database from a book's content through sequential extraction,
    with explicit ID assignments and references between extraction steps.
    """
    def __init__(self,
                 chat_model,
                 entity_types=None,
                 relationship_types=None,
                 entity_prompts_map=None,
                 relationship_prompts_map=None,
                 reference_mappings=None,
                 book_text="",
                 status_callback=None): 
        self.chat_model = chat_model
        self.book_text = book_text
        self.book_metadata = None
        self.status_callback = status_callback 


        # Set entity types and prompt maps
        self.entity_types = entity_types or []
        self.relationship_types = relationship_types or []
        self.entity_prompts_map = entity_prompts_map or {}
        self.relationship_prompts_map = relationship_prompts_map or {}
        self.reference_mappings = reference_mappings or {}

        # Initialize extracted data structures
        self.extracted_entities = {
            entity_type.name: [] for entity_type in self.entity_types
        }
        self.extracted_relationships = {
            rel_type.name: [] for rel_type in self.relationship_types
        }

        # Add metadata to extraction status
        self.extraction_status = {
            "metadata": "not_started",
            **{entity_type.name: "not_started" for entity_type in self.entity_types},
            **{rel_type.name: "not_started" for rel_type in self.relationship_types}
        }

        self.book_chat_history = []
        self.collections_created = False
        logging.debug("EntityRelationshipExtractor initialized with Chat model")
        
    # --- Add a helper method for updating status ---
    def _update_status(self, message):
        if self.status_callback:
            try:
                self.status_callback(message)
                logging.info(f"Status Update: {message}") # Also log it
            except Exception as e:
                # Avoid crashing the thread if callback fails
                logging.error(f"Status callback failed: {e}")     

    def set_book_text(self, text: str) -> None:
        self.book_text = text
        logging.debug(f"Book text set (length: {len(text)} characters)")

    # Print the current state of the class
    def print_state(self):
        print("Entity Types:", self.entity_types)
        print("Relationship Types:", self.relationship_types)

        print(" - " * 20)
        # For dictionaries, slice the items after converting to a list
        entity_items = list(self.entity_prompts_map.items())[:3]
        relationship_items = list(self.relationship_prompts_map.items())[:3]
        print("Entity Prompts Map (first 3 items):", entity_items)
        print("Relationship Prompts Map (first 3 items):", relationship_items)

        print(" + " * 20)
        print("Extraction Status:", self.extraction_status)

        print(" * " * 20)
        print("Extracted Entities:", self.extracted_entities)
        print("Extracted Relationships:", self.extracted_relationships)

    def ask_book(self, prompt: str, role: str = "user", parse_json=True):
        self.book_chat_history.append({"role": role, "content": prompt})
        messages = []
        for msg in self.book_chat_history:
            if msg["role"] == "system":
                messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
        try:
            response = self.chat_model.invoke(messages)
            result = response.content
            self.book_chat_history.append({"role": "assistant", "content": result})
            if parse_json:
                try:
                    cleaned = self._clean_json_string(result)
                    logging.debug(f"Cleaned JSON: {cleaned[:100]}...")
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    logging.warning("Could not parse result as JSON in ask_book")
                    return {"error": "Failed to parse response as JSON", "raw_result": result}
            return result
        except Exception as e:
            err = f"Error in ask_book: {str(e)}"
            logging.error(err)
            return {"error": err}

    def _chat_extract(self, messages, parse_json=True):
        """
        Synchronous version of chat extraction
        """
        formatted = []
        for m in messages:
            if m["role"] == "system":
                formatted.append({"role": "system", "content": m["content"]})
            elif m["role"] == "user":
                formatted.append({"role": "user", "content": m["content"]})
            elif m["role"] == "assistant":
                formatted.append({"role": "assistant", "content": m["content"]})

        try:

            response = self.chat_model.invoke(formatted)
            
            result = response.content

            logging.debug("RESPONSE::::")
            logging.debug(result)

            if parse_json:
                try:
                    cleaned = clean_json_string(result)
                    logging.debug(f"Cleaned JSON: {cleaned[:100]}...")
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    logging.warning("Could not parse result as JSON")
                    return {"error": "Failed to parse response as JSON", "raw_result": result}
            return result
        except Exception as e:
            err = f"Error in chat extraction: {str(e)}"
            logging.error(err)
            return {"error": err}

    def _extract_entity(self, entity_type, id_prefix=None):
        """
        Generic function for extracting an entity type
        """
        if not self.book_text:
            return {"error": "No book text available for analysis"}

        entity_name = entity_type.name
        self.extraction_status[entity_name] = "in_progress"
        self._update_status(f"Extracting {entity_name}...")

        
        system_prompt = self.entity_prompts_map.get(entity_type, "")
        if not system_prompt:
            self.extraction_status[entity_name] = "failed"
            err = f"No prompt found for entity type {entity_name}"
            logging.error(err)
            self._update_status(f"Error: No prompt for {entity_name}.")

            return {"error": err}

        user_prompt = f"Extract all {entity_name.lower()}s from the book and return a JSON array:\nBook:\n{self.book_text}"

        logging.debug(f"{entity_name.upper()}::::")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            data = self._chat_extract(messages)

            if isinstance(data, dict) and "error" in data:
                self.extraction_status[entity_name] = "failed"
                self._update_status(f"Failed to extract {entity_name}.") 
                return data

            # Add _key to each entity
            if id_prefix:
                for i, item in enumerate(data):
                    item["_key"] = f"{id_prefix}_{i+1:02d}"
            else:
                for i, item in enumerate(data):
                    item["_key"] = f"{entity_name[:4]}_{i+1:02d}"

            self.extracted_entities[entity_name] = data
            self.extraction_status[entity_name] = "completed"
            logging.debug(f"Extracted {len(data)} {entity_name}")
            self._update_status(f"Completed extraction for {entity_name} ({len(data)} found).") 
            return {entity_name: data}
        
        except Exception as e:
            self.extraction_status[entity_name] = "failed"
            err = f"Error extracting {entity_name}: {str(e)}"
            logging.error(err)
            self._update_status(f"Error during {entity_name} extraction: {e}")
            return {"error": err}

    def _build_reference_for(self, entity_key, transform=None):
        """
        Creates a reference JSON for a specific entity type
        """
        if not transform:
            transform = lambda item: {
                "_key": item["_key"],
                "name": item.get("name", "Unknown")
            }

        return json.dumps([transform(item) for item in self.extracted_entities[entity_key]], indent=2)

    def _get_entity_references(self, relationship_type):
        """
        Determines which entity references are needed for a relationship type
        """
        # This would be a mapping you'd define based on the relationship type
        # Example mapping for different relationship types

        return self.reference_mappings.get(relationship_type.name, {})

    def _extract_relationship_async(self, relationship_type):
        """
        Generic function for extracting a relationship type
        """
        rel_name = relationship_type.name
        self.extraction_status[rel_name] = "in_progress"
        self._update_status(f"Extracting relationships: {rel_name}...")

        system_prompt = self.relationship_prompts_map.get(relationship_type, "")
        if not system_prompt:
            self.extraction_status[rel_name] = "failed"
            err = f"No prompt found for relationship type {rel_name}"
            logging.error(err)
            self._update_status(f"Error: No prompt for {rel_name}.")
            return {"error": err}

        # Get required entity references for this relationship type
        required_refs = self._get_entity_references(relationship_type)

        # Check if all required entities are available
        for ref_key, (entity_key, _) in required_refs.items():
            entity_data = self.extracted_entities.get(entity_key, [])
            if not entity_data:
                self.extraction_status[rel_name] = "failed"
                err = f"Required entity {entity_key} missing for {rel_name}"
                logging.error(err)
                self._update_status(f"Error: Missing entity {entity_key} for {rel_name}.")
                return {"error": err}

        # Build reference strings for each required entity
        refs = {}
        for ref_key, (entity_key, transform_func) in required_refs.items():
            refs[ref_key] = self._build_reference_for(entity_key, transform_func)

        # Create a base prompt that includes references
        base_prompt = f"Extract information from the Book:\n{self.book_text}"
        for ref_key, ref_data in refs.items():
            base_prompt = f"Using reference for {ref_key}:\n```json\n{ref_data}\n```\n{base_prompt}"

        logging.debug(f"{rel_name.upper()}::::")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": base_prompt}
        ]

        try:
            data = self._chat_extract(messages)

            if isinstance(data, dict) and "error" in data:
                self.extraction_status[rel_name] = "failed"
                self._update_status(f"Failed to extract {rel_name} relationships.") 
                return data

            self.extracted_relationships[rel_name] = data
            self.extraction_status[rel_name] = "completed"
            logging.debug(f"Extracted {len(data)} {rel_name} relationships")
            self._update_status(f"Completed extraction for {rel_name} relationships ({len(data)} found).")
            return {rel_name: data}
        
        except Exception as e:
            self.extraction_status[rel_name] = "failed"
            err = f"Error extracting {rel_name} relationships: {str(e)}"
            logging.error(err)
            self._update_status(f"Error during {rel_name} extraction: {e}")
            return {"error": err}

    def _extract_book_metadata_async(self):
        """
        Function to extract book metadata and store it as a BookMetadata instance.
        """
        if not self.book_text:
            return {"error": "No book text available for analysis"}

        self.extraction_status["metadata"] = "in_progress"
        self._update_status("Extracting book metadata...")

        messages = [
            {"role": "system", "content": """
                You are a literary analyst tasked with extracting metadata from books.
                Extract only the requested fields and return them in JSON format as follows:
                book_name, author, pages_count, time_to_process, summary
            """},
            {"role": "user", "content": f"Return ONLY a JSON object and nothing else.\nBook text:\n{self.book_text}"}
        ]

        try:
            logging.debug("Metadata::::")
            result = self._chat_extract(messages)
            if "error" in result:
                self.extraction_status["metadata"] = "failed"
                self._update_status("Failed to extract book metadata.")
                
                return result

            # Convert the JSON dict into a BookMetadata instance
            self.book_metadata = BookMetadata(
                book_name=result.get("book_name", "Unknown"),
                author=result.get("author", "Unknown"),
                pages_count=result.get("pages_count", 0),
                time_to_process=result.get("time_to_process", "Unknown"),
                summary=result.get("summary", "")
            )
            self.extraction_status["metadata"] = "completed"
            self.book_chat_history = messages.copy()

            # Update the global CURRENT_BOOK_METADATA variable
            global CURRENT_BOOK_METADATA
            CURRENT_BOOK_METADATA = BookMetadata(
                book_name=self.book_metadata.book_name,
                author=self.book_metadata.author,
                pages_count=self.book_metadata.pages_count,
                time_to_process=0,
                summary=self.book_metadata.summary,
                )

            logging.debug(f"Book metadata extracted: {self.book_metadata}")
            self._update_status("Book metadata extracted.")

            return self.book_metadata
        except Exception as e:
            self.extraction_status["metadata"] = "failed"
            err = f"Error extracting book metadata: {str(e)}"
            logging.error(err)
            return {"error": err}

    def extract_all_items(self):
        """
        Run the complete extraction process synchronously for both entities and relationships.
        """
        self._update_status("Starting full extraction process...") 
        
        # First extract metadata
        metadata_result = self._extract_book_metadata_async()
        if isinstance(metadata_result, dict) and "error" in metadata_result:
            logging.error("Metadata extraction failed; continuing with other extractions.")

        # 🔒 guard -------------------------------------------------------------
        if self.book_metadata is not None:
            cached = cache_load(self.book_metadata.book_name, self.book_text)
            if cached:
                self.extracted_entities      = cached["entities_map"]
                self.extracted_relationships = cached["relationships_map"]
                self._update_status("Loaded entities/relationships from cache ✅")
                return self._finalise()
        # --------------------------------------------------------------------
        
        # 0️⃣  try the cache first  ------------------------------------------
        cached = cache_load(self.book_metadata.book_name, self.book_text)
        if cached:
            self.extracted_entities     = cached["entities_map"]
            self.extracted_relationships = cached["relationships_map"]
            self._update_status("Loaded entities/relationships from cache ✅")
            return self._finalise()
        # -------------------------------------------------------------------


        # Extract all entity types in parallel
        entity_tasks = []
        self._update_status("Starting entity extraction...")
        for entity_type in self.entity_types:
            # Generate id_prefix from entity type name
            id_prefix = entity_type.name[:4]
            task = self._extract_entity(entity_type, id_prefix)
            entity_tasks.append(task)

        # Process entity results
        for i, result in enumerate(entity_tasks):
            if isinstance(result, Exception):
                entity_type = self.entity_types[i]
                logging.error(f"Error extracting {entity_type.name}: {str(result)}")
                self.extraction_status[entity_type.name] = "failed"
        self._update_status("Entity extraction phase complete.")

        # Extract all relationship types in parallel
        relationship_tasks = []
        self._update_status("Starting relationship extraction...")
        for rel_type in self.relationship_types:
            task = self._extract_relationship_async(rel_type)
            relationship_tasks.append(task)

        # Process relationship results
        for i, result in enumerate(relationship_tasks):
            if isinstance(result, Exception):
                rel_type = self.relationship_types[i]
                logging.error(f"Error extracting {rel_type.name}: {str(result)}")
                self.extraction_status[rel_type.name] = "failed"
        self._update_status("Relationship extraction phase complete.") 

        # 1️⃣  after successful extraction, stash it  ------------------------
        cache_save(self.book_metadata.book_name, self.book_text,
                   self.extracted_entities, self.extracted_relationships)
        # -------------------------------------------------------------------
        return self._finalise()


    def extract_all(self):
       
        """
        Run the complete extraction process synchronously for both entities and relationships.
        """
        return self.extract_all_items()
    
    def _finalise(self):
        global CURRENT_BOOK_METADATA
        UPDATED = CURRENT_BOOK_METADATA.update_maps(
            self.extracted_entities, self.extracted_relationships)
        self.book_metadata = UPDATED or CURRENT_BOOK_METADATA
        CURRENT_BOOK_METADATA = self.book_metadata
        self._update_status("Extraction process finished.")
        return self.extracted_entities, self.extracted_relationships