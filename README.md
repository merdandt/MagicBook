# MagicBook: Dynamic Book Relationship Visualization System

MagicBook is a cutting-edge tool that transforms literary analysis by dynamically visualizing intricate narrative relationships. Leveraging advanced natural language processing and network analysis, the system extracts key entities from texts and converts them into interactive graphs, offering an innovative way to explore literature.

## Features

- **Interactive Graph Visualization**: Explore complex book relationships with an interactive graph interface
- **Entity Extraction**: Automatically identify characters, locations, events, and more from book text
- **Relationship Mapping**: Discover connections between entities in the narrative
- **Book Caching**: Save and reload previously analyzed books
- **Entity Explorer**: Deep-dive into specific entities and their relationships
- **Analysis Dashboard**: Gain insights with visual analytics of book structure
- **ArangoDB Integration**: Store and query book graphs in a graph database

## Installation

### Prerequisites

- Python 3.8+
- [ArangoDB](https://www.arangodb.com/) (optional for graph storage)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/magicbook.git
cd magicbook
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
magicbook/
├── app.py                 # Main Streamlit entry point
├── requirements.txt       # Dependencies
├── README.md
├── data/                  # Directory for cached books
├── utils/
│   ├── __init__.py
│   ├── file_utils.py      # PDF processing, file handling
│   ├── embedding.py       # Embedding generation
│   └── graph_utils.py     # Graph operations
├── models/
│   ├── __init__.py
│   ├── book_metadata.py   # BookMetadata class
│   └── entity_types.py    # Entity and relationship types
├── core/
│   ├── __init__.py
│   ├── extractor.py       # Entity and relationship extraction
│   ├── graph_builder.py   # Build NetworkX graphs
│   └── visualizer.py      # Graph visualization
└── services/
    ├── __init__.py
    ├── cache_service.py   # Book caching
    ├── graph_service.py   # Graph processing
    └── db_service.py      # ArangoDB integration
```

## Usage

1. **Book Selection**:
   - Upload a new PDF book or select a previously cached book
   - The system will extract entities and relationships from the text

2. **Graph Visualization**:
   - Explore the interactive graph of entities and their relationships
   - Zoom, pan, and click on nodes to see details

3. **Entity Explorer**:
   - Browse entities by type (characters, locations, events, etc.)
   - View detailed information about specific entities
   - Explore relationships involving selected entities

4. **Analysis**:
   - View entity and relationship distributions
   - Explore network statistics and community structures
   - See text-based representations of entities and relationships

5. **Settings**:
   - Configure database connections
   - Manage cached books
   - Export graphs to ArangoDB

## Advanced Features

### ArangoDB Integration

MagicBook can store and query book graphs in ArangoDB, a high-performance NoSQL graph database. To enable this feature:

1. Install ArangoDB following the [official instructions](https://www.arangodb.com/download-major/)
2. Configure the database connection in the Settings tab
3. Upload book graphs to ArangoDB for persistent storage and advanced querying

### Custom Entity and Relationship Types

The system supports a wide range of entity and relationship types for literary analysis:

- **Entity Types**: Character, Location, Chapter, Event, Item, Organization, Concept, Creature, TimePeriod
- **Relationship Types**: Family relationships, emotional bonds, interactions, spatial connections, event participation, and many more

## Limitations

- The current entity extraction capability is limited to placeholder functionality and requires integration with a production-ready NLP system or LLM
- Performance may vary depending on book size and complexity
- Graph visualization can become crowded with very large books
- ArangoDB integration requires a separate database installation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NetworkX for graph data structures
- Streamlit for the interactive web interface
- Plotly for interactive visualizations
- Sentence Transformers for text embeddings