class BookMetadata:
    """
    Class representing metadata of a book, including extracted entities and relationships.
    """
    def __init__(self, book_name, author, pages_count, time_to_process, summary):
        self.book_name = book_name
        self.author = author
        self.pages_count = pages_count
        self.time_to_process = time_to_process
        self.summary = summary
        # Maps containing extracted entities and relationships
        self.entities_map = None
        self.relationships_map = None
    
    @classmethod
    def from_txt(cls, txt):
        """
        Create a BookMetadata instance by parsing a text block.
        Expected format:
        Book Name: <name>
        Author: <author>
        Pages Count: <number>
        Time to Process: <time>
        Summary: <summary text>
        """
        lines = txt.strip().splitlines()
        data = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        return cls(
            book_name=data.get("Book Name", ""),
            author=data.get("Author", ""),
            pages_count=data.get("Pages Count", ""),
            time_to_process=data.get("Time to Process", ""),
            summary=data.get("Summary", "")
        )
    
    def update_maps(self, entities_map, relationships_map):
        """Update entities and relationships maps"""
        self.entities_map = entities_map
        self.relationships_map = relationships_map
    
    def __str__(self):
        return (f"Book Name: {self.book_name}\n"
                f"Author: {self.author}\n"
                f"Pages Count: {self.pages_count}\n"
                f"Time to Process: {self.time_to_process}\n"
                f"Summary: {self.summary}\n"
                f"Entities: {len(self.entities_map) if self.entities_map else 0} types\n"
                f"Relationships: {len(self.relationships_map) if self.relationships_map else 0} types")
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "book_name": self.book_name,
            "author": self.author,
            "pages_count": self.pages_count,
            "time_to_process": self.time_to_process,
            "summary": self.summary,
            "entities_map": self.entities_map,
            "relationships_map": self.relationships_map
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        instance = cls(
            book_name=data.get("book_name", ""),
            author=data.get("author", ""),
            pages_count=data.get("pages_count", ""),
            time_to_process=data.get("time_to_process", ""),
            summary=data.get("summary", "")
        )
        instance.entities_map = data.get("entities_map")
        instance.relationships_map = data.get("relationships_map")
        return instance