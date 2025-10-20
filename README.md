# Hybrid Chat System for Vietnam Travel Dataset

A hybrid chatbot system that combines graph database (Neo4j) and vector database (Pinecone) capabilities to provide intelligent responses about Vietnam travel destinations. This project demonstrates the integration of structured relationship queries with semantic search, complete with an automated evaluation framework for assessing system performance.

## Overview

This system leverages two complementary database technologies:

- **Neo4j Graph Database**: Stores structured relationships between cities, attractions, hotels, and activities
- **Pinecone Vector Database**: Enables semantic search through text embeddings for meaning-based queries

By combining both approaches, the system can handle factual queries ("What hotels are in Hanoi?"), semantic queries ("Find romantic beach resorts"), and complex hybrid queries that require both relationship traversal and semantic understanding.

The project includes a comprehensive evaluation framework that automatically tests the system across multiple query types and generates detailed performance reports.

## Architecture

The project consists of several key components:

### Data Pipeline

- `vietnam_travel_dataset.json`: Source dataset containing 360 travel entities
- `load_to_neo4j.py`: Loads entities and relationships into Neo4j graph database
- `pinecone_upload.py`: Generates embeddings and uploads to Pinecone vector database

### Query System

- `hybrid_chat.py`: Main chatbot interface that routes queries to appropriate databases
- `config.py`: Configuration file for API credentials and connection settings

### Evaluation Framework

- `generate_test_conversations.py`: Creates diverse test queries and generates system responses
- `automated_evaluation.py`: Automated evaluation system with scoring algorithms
- `generate_report.py`: Generates comprehensive evaluation reports
- `test_conversations.json`: Generated test conversations with responses
- `evaluation_results.json`: Detailed evaluation scores and analysis
- `evaluation_summary.json`: Summary statistics and key findings
- `EVALUATION_REPORT.md`: Final comprehensive evaluation report

### Visualization

- `visualize_graph.py`: Generates visual representations of the Neo4j graph structure
- `neo4j_viz.html`: Interactive graph visualization output
- `test.py`: Connection testing utility for all services

## Features

- **Graph-based Queries**: Traverse relationships between entities (e.g., hotels in a city, attractions near landmarks)
- **Semantic Search**: Find entities based on meaning and context using vector embeddings
- **Hybrid Intelligence**: Combine structured and unstructured data retrieval for complex queries
- **Interactive Visualizations**: Explore the knowledge graph structure visually

## Dataset

The Vietnam travel dataset includes:

- 10 major cities (Hanoi, Ha Long, Sapa, Hue, Hoi An, Da Nang, Nha Trang, Da Lat, Ho Chi Minh City, Mekong Delta)
- 235+ attractions, hotels, restaurants, and activities
- Rich metadata including descriptions, tags, and semantic text
- Structured relationships (Located_In, Connected_To, Near, etc.)

## Prerequisites

- Python 3.9 or higher
- Neo4j database (local installation or Neo4j Aura cloud instance)
- Pinecone account with API key
- OpenAI API key for generating embeddings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vietnam-travel-hybrid-chat.git
cd vietnam-travel-hybrid-chat
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd hybrid_chat_test
pip install -r requirements.txt
```

4. Configure credentials:
Edit `config.py` with your API keys and database credentials:
```python
NEO4J_URI = "your-neo4j-uri"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"

OPENAI_API_KEY = "your-openai-api-key"

PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "vietnam-travel"
PINECONE_VECTOR_DIM = 1536
```

## Usage

### Initial Setup

1. Load data into Neo4j:

```bash
python load_to_neo4j.py
```

2. Upload embeddings to Pinecone:

```bash
python pinecone_upload.py
```

3. Test all connections:

```bash
python test_connections.py
```

### Running the Chat System

Test the hybrid chat system with sample queries:

```bash
python hybrid_chat.py
```

### Running the Complete Evaluation

Execute the full evaluation pipeline:

```bash
# Step 1: Generate test conversations
python generate_test_conversations.py

# Step 2: Run automated evaluation
python automated_evaluation.py

# Step 3: Generate comprehensive report
python generate_report.py
```

This will create:
- `test_conversations.json`: 12 test queries with system responses
- `evaluation_results.json`: Detailed scores and analysis for each conversation
- `evaluation_summary.json`: Summary statistics
- `EVALUATION_REPORT.md`: Comprehensive markdown report

### Visualizing the Graph

Generate an interactive visualization of the Neo4j graph:

```bash
python visualize_graph.py
```

This will generate `neo4j_viz.html` which can be opened in a web browser.

## Query Examples

### Factual Queries (Neo4j)
- "What attractions are in Hanoi?"
- "Show me hotels near Ha Long Bay"
- "List restaurants in Hoi An"

### Semantic Queries (Pinecone)
- "Find romantic places for honeymoon"
- "Recommend budget-friendly mountain accommodations"
- "Best locations for adventure activities"

### Hybrid Queries
- "Plan a romantic 3-day trip in Da Nang"
- "Find luxury beach hotels with cultural experiences nearby"
- "Suggest family-friendly activities in Ho Chi Minh City"

## Project Structure

```
hybrid_chat_test/
├── config.py                          # Configuration and API keys
├── vietnam_travel_dataset.json        # Source data (360 entities)
│
├── Data Loading
├── load_to_neo4j.py                  # Neo4j data loader
├── pinecone_upload.py                # Pinecone embedding uploader
│
├── Core System
├── hybrid_chat.py                    # Main chatbot interface
├── test.py                           # Connection testing utility
│
├── Evaluation Pipeline
├── generate_test_conversations.py    # Generate test queries and responses
├── automated_evaluation.py           # Automated evaluation framework
├── generate_report.py                # Report generation
├── test_conversations.json           # Generated test data
├── evaluation_results.json           # Evaluation scores
├── evaluation_summary.json           # Summary statistics
├── EVALUATION_REPORT.md              # Final report
│
├── Visualization
├── visualize_graph.py                # Graph visualization generator
├── neo4j_viz.html                    # Interactive graph output
│
└── requirements.txt                   # Python dependencies
```

## How It Works

### 1. Data Loading Phase

**Neo4j (`load_to_neo4j.py`)**:
- Reads `vietnam_travel_dataset.json`
- Creates nodes for each entity (cities, hotels, attractions)
- Establishes relationships between entities
- Creates graph constraints for data integrity

**Pinecone (`pinecone_upload.py`)**:
- Processes each entity's text content
- Generates embeddings using OpenAI's text-embedding-ada-002
- Uploads vectors with metadata to Pinecone index
- Enables semantic similarity search

### 2. Query Processing Phase

**Hybrid Chat System (`hybrid_chat.py`)**:
- Receives user query
- Classifies query type (graph, semantic, or hybrid)
- Routes to appropriate database(s):
  - **Graph queries**: Uses Neo4j Cypher queries for structured data
  - **Semantic queries**: Uses Pinecone vector search for meaning-based retrieval
  - **Hybrid queries**: Combines results from both databases
- Formats and returns response

### 3. Evaluation Phase

**Test Generation (`generate_test_conversations.py`)**:
- Creates 12 diverse test queries across categories:
  - Graph queries (factual, structural)
  - Semantic queries (meaning-based)
  - Hybrid queries (complex, multi-source)
  - Edge cases
- Runs each query through the hybrid chat system
- Saves queries and responses to `test_conversations.json`

**Automated Evaluation (`automated_evaluation.py`)**:
- Evaluates each conversation on four metrics:
  - **Source Correctness** (30%): Did it use the right database(s)?
  - **Response Length** (20%): Is the response substantial?
  - **Entity Count** (25%): How many relevant results?
  - **Query Match** (25%): Does response address the query?
- Calculates weighted overall scores
- Generates analysis and feedback
- Saves to `evaluation_results.json`

**Report Generation (`generate_report.py`)**:
- Analyzes evaluation results
- Calculates statistics by category
- Identifies top performers and areas for improvement
- Generates comprehensive `EVALUATION_REPORT.md`
- Creates summary JSON with key metrics

## Technical Details

### Neo4j Schema

**Node Labels:**
- City
- Attraction
- Hotel
- Restaurant
- Activity
- Entity (base label for all nodes)

**Relationship Types:**
- Located_In
- Connected_To
- Near
- Part_Of

**Properties:**
- id (unique identifier)
- name
- type
- description
- region
- tags
- Additional entity-specific properties

### Pinecone Index

**Configuration:**
- Dimension: 1536 (OpenAI text-embedding-3-small)
- Metric: Cosine similarity
- Cloud: AWS
- Region: us-east-1

**Metadata:**
- name
- type
- description
- region
- tags


## Evaluation Methodology

### Automated Scoring System

The evaluation framework uses a weighted scoring algorithm:

**Metrics and Weights:**
- Source Correctness (30%): Validates database selection against expected sources
- Response Length (20%): Ensures responses are substantial and informative
- Entity Count (25%): Measures completeness through number of results returned
- Query Match (25%): Assesses semantic relevance to the original query

**Scoring Scale:** 1-5 for each metric
- 5: Excellent performance
- 4: Good performance
- 3: Acceptable performance
- 2: Poor performance
- 1: Failed or no results

### Test Coverage

The test suite includes:
- **3 Graph queries**: Testing structured relationship traversal
- **4 Semantic queries**: Testing meaning-based search capabilities
- **3 Hybrid queries**: Testing integration of both systems
- **2 Edge cases**: Testing boundary conditions and error handling

### Report Outputs

The evaluation generates three key deliverables:

1. **evaluation_results.json**: Raw scores, detailed analysis for each conversation
2. **evaluation_summary.json**: Aggregate statistics, top/low performers, category breakdown
3. **EVALUATION_REPORT.md**: Comprehensive analysis with recommendations

## Key Features Explained

### Query Classification

The system automatically determines query type based on linguistic patterns:
- **Graph indicators**: "in", "near", "located", "what are", "list", "show"
- **Semantic indicators**: "romantic", "best", "recommend", "authentic", "luxury"
- **Hybrid indicators**: "plan", "itinerary", "trip", complex multi-clause queries

### Hybrid Intelligence

When both databases are used:
1. Neo4j provides structured context (locations, relationships)
2. Pinecone provides semantic matches (qualities, attributes)
3. Results are merged with intelligent ranking
4. Response combines factual accuracy with relevance

### Performance Optimization

- Batch processing for Pinecone uploads (100 vectors at a time)
- Cypher query optimization with parameterized queries
- Connection pooling for database efficiency
- Result caching to avoid redundant API calls

## License

MIT License

## Contributing

Contributions are welcome. Please submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

- Dataset curated for educational purposes focusing on Vietnam tourism
- Built using Neo4j graph database, Pinecone vector database, and OpenAI embeddings
- Part of AI Hybrid Chat Evaluation assignment
- Demonstrates practical application of hybrid retrieval systems

## Results Summary

After running the complete evaluation pipeline, you can expect:

- Overall system performance score (typically 3.5-4.5/5.0)
- Source selection accuracy metrics
- Performance breakdown by query category
- Identification of system strengths and weaknesses
- Actionable recommendations for improvements

The evaluation report provides a comprehensive analysis suitable for academic submission or technical documentation.


## Future Enhancements

Potential improvements to the system:

1. Implement user feedback loop for continuous learning
2. Add natural language generation for more conversational responses
3. Integrate real-time data updates
4. Support multi-language queries
5. Add filtering by price, ratings, and availability
6. Implement conversation context and follow-up questions
7. Create REST API for web/mobile integration

## Contact

For questions or collaboration opportunities, please open an issue in the repository.

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Status**: Complete with evaluation framework
