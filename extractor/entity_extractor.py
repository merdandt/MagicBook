import asyncio
import json
from flask import logging

from utils.book_meta_data import BookMetadata
from utils.json_functions import clean_json_string


class AsyncEntityRelationshipExtractor:
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
                 reference_mappings = None,
                 book_text=""
                 ):
        self.chat_model = chat_model
        self.book_text = book_text
        self.book_metadata = None

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

    async def _chat_extract_async(self, messages, parse_json=True):
        """
        Async version of chat extraction
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
            # For async implementation, you might need to use a different async client
            # This is a placeholder for the async call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: self.chat_model.invoke(formatted)
            )
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

    async def _extract_entity_async(self, entity_type, id_prefix=None):
        """
        Generic async function for extracting an entity type
        """
        if not self.book_text:
            return {"error": "No book text available for analysis"}

        entity_name = entity_type.name
        self.extraction_status[entity_name] = "in_progress"

        system_prompt = self.entity_prompts_map.get(entity_type, "")
        if not system_prompt:
            self.extraction_status[entity_name] = "failed"
            err = f"No prompt found for entity type {entity_name}"
            logging.error(err)
            return {"error": err}

        user_prompt = f"Extract all {entity_name.lower()}s from the book and return a JSON array:\nBook:\n{self.book_text}"

        logging.debug(f"{entity_name.upper()}::::")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            data = await self._chat_extract_async(messages)

            if isinstance(data, dict) and "error" in data:
                self.extraction_status[entity_name] = "failed"
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
            return {entity_name: data}
        except Exception as e:
            self.extraction_status[entity_name] = "failed"
            err = f"Error extracting {entity_name}: {str(e)}"
            logging.error(err)
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

    async def _extract_relationship_async(self, relationship_type):
        """
        Generic async function for extracting a relationship type
        """
        rel_name = relationship_type.name
        self.extraction_status[rel_name] = "in_progress"

        system_prompt = self.relationship_prompts_map.get(relationship_type, "")
        if not system_prompt:
            self.extraction_status[rel_name] = "failed"
            err = f"No prompt found for relationship type {rel_name}"
            logging.error(err)
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

        print(': : ' * 20)
        print(messages)
        print(': : ' * 20)

        try:
            data = await self._chat_extract_async(messages)

            if isinstance(data, dict) and "error" in data:
                self.extraction_status[rel_name] = "failed"
                return data

            self.extracted_relationships[rel_name] = data
            self.extraction_status[rel_name] = "completed"
            logging.debug(f"Extracted {len(data)} {rel_name} relationships")
            return {rel_name: data}
        except Exception as e:
            self.extraction_status[rel_name] = "failed"
            err = f"Error extracting {rel_name} relationships: {str(e)}"
            logging.error(err)
            return {"error": err}

    async def _extract_book_metadata_async(self):
        """
        Async function to extract book metadata and store it as a BookMetadata instance.
        """
        if not self.book_text:
            return {"error": "No book text available for analysis"}

        self.extraction_status["metadata"] = "in_progress"
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
            result = await self._chat_extract_async(messages)
            if "error" in result:
                self.extraction_status["metadata"] = "failed"
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
            return self.book_metadata
        except Exception as e:
            self.extraction_status["metadata"] = "failed"
            err = f"Error extracting book metadata: {str(e)}"
            logging.error(err)
            return {"error": err}

    async def extract_all_async(self):
        """
        Run the complete extraction process asynchronously for both entities and relationships.
        """
        # First extract metadata
        metadata_result = await self._extract_book_metadata_async()
        if isinstance(metadata_result, dict) and "error" in metadata_result:
            logging.error("Metadata extraction failed; continuing with other extractions.")

        # Extract all entity types in parallel
        entity_tasks = []
        for entity_type in self.entity_types:
            # Generate id_prefix from entity type name
            id_prefix = entity_type.name[:4]
            task = self._extract_entity_async(entity_type, id_prefix)
            entity_tasks.append(task)

        # Wait for all entity extractions to complete
        entity_results = await asyncio.gather(*entity_tasks, return_exceptions=True)

        # Process entity results
        for i, result in enumerate(entity_results):
            if isinstance(result, Exception):
                entity_type = self.entity_types[i]
                logging.error(f"Error extracting {entity_type.name}: {str(result)}")
                self.extraction_status[entity_type.name] = "failed"

        # Extract all relationship types in parallel
        relationship_tasks = []
        for rel_type in self.relationship_types:
            task = self._extract_relationship_async(rel_type)
            relationship_tasks.append(task)

        # Wait for all relationship extractions to complete
        relationship_results = await asyncio.gather(*relationship_tasks, return_exceptions=True)

        # Process relationship results
        for i, result in enumerate(relationship_results):
            if isinstance(result, Exception):
                rel_type = self.relationship_types[i]
                logging.error(f"Error extracting {rel_type.name}: {str(result)}")
                self.extraction_status[rel_type.name] = "failed"

        global CURRENT_BOOK_METADATA
        CURRENT_BOOK_METADATA = CURRENT_BOOK_METADATA.update_maps(self.extracted_entities, self.extracted_relationships)

        return (self.extracted_entities, self.extracted_relationships)

    def extract_all(self):
        """
        Synchronous wrapper for extract_all_async.
        """
        # Create and run the event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.extract_all_async())
        finally:
            loop.close()