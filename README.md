
# 🌊 Marine Sensor KG-RAG

A Knowledge Graph-based Retrieval-Augmented Generation (KG-RAG) application for answering technical questions about marine instrumentation and sensors.

## Project Overview

This project uses the Endress+Hauser Micropilot FMR51 technical manual to build a knowledge graph and provide natural-language answers with supporting evidence and PDF page references.

## Features

- PDF document loading
- AI-based entity extraction
- Relationship extraction and mapping
- Knowledge graph storage using Neo4j AuraDB
- Natural-language question classification
- Graph-based information retrieval
- AI-generated technical answers
- Source evidence and PDF page references
- Interactive Streamlit chat interface

## Architecture

PDF Manual
    ↓
Document Loader
    ↓
Entity Extraction
    ↓
Relationship Mapping
    ↓
Data Cleaning and Normalization
    ↓
Neo4j Knowledge Graph
    ↓
Question Classification
    ↓
Graph Retrieval
    ↓
GPT-4.1-mini Answer Generation
    ↓
Streamlit Web Application

## Technologies Used

- Python 3.13
- LangChain
- OpenAI GPT-4.1-mini
- Neo4j AuraDB
- Streamlit
- Pydantic
- PyPDFLoader

## Project Structure

Marine_KG_RAG/
│
├── documents/
│   └── FMR51_manual.pdf
│
├── document_loader.py
├── entity_extractor.py
├── relationship_mapper.py
├── relationship_cleaner.py
├── normalize_graph_data.py
├── graph_storage.py
├── graph_query.py
├── kg_qa.py
├── app.py
│
├── entities.json
├── relationships.json
├── cleaned_relationships.json
├── normalized_entities.json
├── normalized_relationships.json
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md

## Installation

### 1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

### 2. Navigate to the project folder

cd Marine_KG_RAG

### 3. Create a virtual environment

python -m venv venv

### 4. Activate the environment (Windows)

venv\Scripts\activate

### 5. Install dependencies

pip install -r requirements.txt

### 6. Configure environment variables

Create a `.env` file in the project root:

OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

Use your own credentials. Never upload `.env` to GitHub.

### 7. Run the application

streamlit run app.py

Open the local URL displayed in your terminal, usually:

http://localhost:8501

## Example Questions

- What is the measurement range of Micropilot FMR51?
- Who is the manufacturer?
- What is the accuracy of the sensor?
- What is the maximum process temperature?
- Which communication protocols are supported?

## Knowledge Graph

The current Neo4j graph contains:

- 78 entity nodes
- 45 relationships

## Future Enhancements

- Support multiple marine sensor manuals
- Add sensor selection and comparison
- Include more technical document formats
- Add network and IoT sensor data integration
- Develop a marine instrumentation technical knowledge assistant

## Author

Rajesh B  
Project Engineer  
NTCPWC – IIT Madras

## Disclaimer

This is an educational and technical knowledge retrieval project. Always verify critical engineering specifications against the original manufacturer's documentation.
