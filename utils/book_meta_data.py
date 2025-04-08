
class BookMetadata:
    def __init__(self, book_name, author, pages_count, time_to_process, summary):
        self.book_name = book_name
        self.author = author
        self.pages_count = pages_count
        self.time_to_process = time_to_process
        self.summary = summary
        # New attributes for JSON maps.
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
    # Update entities_map and relationships_map
    def update_maps(self, entities_map, relationships_map):
        self.entities_map = entities_map
        self.relationships_map = relationships_map

    def __str__(self):
        return (f"Book Name: {self.book_name}\n"
                f"Author: {self.author}\n"
                f"Pages Count: {self.pages_count}\n"
                f"Time to Process: {self.time_to_process}\n"
                f"Summary: {self.summary}\n"
                f"Entities Map: {self.entities_map}\n"
                f"Relationships Map: {self.relationships_map}")