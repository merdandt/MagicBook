# MagicBook: Book Relationship Visualization and Analysis
[Demo](https://magic-book.streamlit.app/)

MagicBook is an AI-powered tool that transforms literary analysis by extracting and visualizing narrative networks from books. Using Google's Gemini AI, it identifies characters, locations, events, and their interconnections, presenting them as interactive graph visualizations that reveal the underlying structure of stories.

## Video explanation
1. https://www.loom.com/share/804ca7a7fb52473aa291f321cfe14ac4?sid=eb22a037-d7c2-4aa7-b2db-b08bd9b09ac2
2. https://www.loom.com/share/2f43dbce3f5941ca8e250a4a072b9b6d?sid=828b9675-df33-41cb-b506-0e864cbd69bb
3. https://www.loom.com/share/38712b2c80cd434fa9a6c96104f018b8?sid=d8f26f70-aa14-4d3d-97ec-4f70203ca369
4. https://www.loom.com/share/815d52b2153f4954872386139f5dbf7a?sid=255033b3-7dea-4eb9-b8fc-dbf8e7d0948c

## How It Works

1. **Upload a Book**: Load a PDF book directly into the application
2. **AI Processing**: Gemini AI models extract entities and relationships from the text
3. **Graph Generation**: Entities and connections are mapped into a network structure
4. **Interactive Exploration**: Navigate the visual representation of the book's narrative elements

## Key Features

- **Multi-tab Interface** with dedicated views for different analytical approaches
- **Interactive Graph Visualization** with color-coded nodes and relationship lines
- **Entity Explorer** for filtering and examining specific characters, locations, or events
- **Relationship Analysis** showing the types and strengths of narrative connections
- **Network Analytics** including centrality measures and community detection
- **Book Caching** for instantly reloading previously analyzed texts
- **Multiple AI Models** with options for balancing speed vs. accuracy

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key for entity extraction

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MagicBook.git
cd MagicBook
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Gemini API key:

The application requires a Google Gemini API key for processing new books. You can:

- Provide the key via environment variable:
  ```bash
  export GEMINI_API_KEY="your-api-key-here"  # On Windows: set GEMINI_API_KEY=your-api-key-here
  ```

- Or enter your API key directly in the application's UI on the "Book Selection" tab.

5. Run the application:
```bash
streamlit run app.py
```

6. Open your browser to http://localhost:8501

## Using MagicBook

1. **Upload a Book**: Select a text or PDF file to analyze
2. **Explore the Graph**: View entities and relationships in the interactive visualization
3. **Entity Inspection**: Click on entities to view their connections and details
4. **Load Sample Data**: Try pre-analyzed books to explore the functionality

## Sample Books

The repository includes pre-analyzed data for:
- Harry Potter and the Philosopher's Stone
- The Fellowship of the Ring
- The Little Prince

## Technical Architecture

- **Streamlit Frontend**: Interactive web interface
- **Gemini Integration**: For entity and relationship extraction
- **NetworkX**: For graph data representation and analysis
- **Plotly**: Powers the interactive visualizations

## Project Structure

```
MagicBook/
├── app.py                 # Main Streamlit application
├── core/                  # Core processing logic
│   ├── extractor.py       # Entity extraction
│   ├── graph_builder.py   # Graph construction
│   ├── visualizer.py      # Visualization tools
│   └── prompts/           # AI prompts for extraction
├── data/                  # Cached book analysis
├── model/                 # Data models
├── services/              # Service layer
├── utils/                 # Utility functions
└── temp_uploads/          # Temporary storage for uploads
```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Gemini for the AI capabilities
- NetworkX for graph data structures
- Streamlit for the web interface
- Plotly for interactive visualizations

## Technical Methodologies and Implementations

### Python Techniques and Libraries
- **Object-Oriented Programming**: Modular architecture with clear class hierarchies and separation of concerns
- **Web Framework**: Streamlit for creating the interactive web application
- **Data Visualization**: Plotly for interactive visualizations, Matplotlib for static graphs
- **Data Manipulation**: Pandas for structured data handling and DataFrames
- **Concurrency**: ThreadPoolExecutor for parallel processing and asyncio for asynchronous operations
- **File Operations**: PathLib for modern path manipulation and handling book uploads
- **Type System**: Enum-based typing for entities and relationships

### AI and ML Techniques
- **Large Language Models**: Integration with Google's Gemini models (1.5 Pro, 2.0 Flash Light, 2.5 Pro Exp)
- **LangChain Framework**: For streamlined LLM interaction and response processing
- **Embedding Models**: Sentence Transformers with 'intfloat/e5-small-v2' for generating entity embeddings
- **Semantic Similarity**: Cosine similarity calculations for entity comparisons
- **Prompt Engineering**: Specialized system and user prompts for entity and relationship extraction
- **Progressive Entity Extraction**: Multi-stage processing methodology with type-specific prompts
- **AI Response Parsing**: Structured extraction of JSON data from LLM outputs

### Graph Theory and Analysis
- **Graph Structures**: Directed multigraphs (NetworkX MultiDiGraph) for representing narrative networks
- **Graph Algorithms**: Centrality measures (degree, betweenness), community detection (Louvain method)
- **Graph Visualization**: Force-directed layouts with node sizing based on importance metrics
- **Graph Database**: ArangoDB integration for persistent storage with AQL query support
- **Network Metrics**: Graph density, connected components, and path analysis
- **Hierarchical Representation**: Structured tree views of narrative elements

### Caching and Data Management
- **Multi-level Caching**: File-based and in-memory caching systems
- **JSON Serialization**: For entity and relationship data persistence
- **Hash-based Caching**: Efficient lookup mechanisms for processed book data
- **Database Operations**: Connection pooling and query optimization

## Next Steps
- Integrate ArangoDB for graph persistence, querying, and scalable storage.
- Build a Natural Language Query Bot that leverages the narrative graph to answer questions like "Which characters interact most with [Entity]?"
- Enable Conversational Exploration of any book: allow users to ask questions and navigate the story through natural language, powered by the underlying graph knowledge.