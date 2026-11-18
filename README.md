# Marine Sensor KG-RAG Assistant
### Knowledge Graph Retrieval-Augmented Generation

An AI-powered technical assistant that answers questions about the **Endress+Hauser Micropilot FMR51 Radar Level Sensor** using a Neo4j Knowledge Graph, PDF source evidence and OpenAI GPT-4.1-mini.

## 1. Project Overview

The Marine Sensor KG-RAG Assistant is designed to extract technical information from sensor documentation, organize it into a Knowledge Graph and provide accurate answers through an interactive chatbot.

Instead of relying only on general LLM knowledge, the application retrieves relevant technical information from Neo4j and uses OpenAI GPT-4.1-mini to generate answers based on the retrieved graph records.

## 2. Project Objectives

- Extract technical specifications from sensor PDF manuals.
- Identify technical entities and relationships.
- Build and store a Knowledge Graph using Neo4j AuraDB.
- Retrieve relevant information using Cypher queries.
- Classify user questions into technical categories.
- Generate answers using OpenAI GPT-4.1-mini.
- Display supporting PDF evidence and page references.
- Provide an interactive chatbot using Streamlit.

## 3. System Architecture

```text
       FMR51 Technical PDF Manual
                  |
                  v
          PDF Text Extraction
                  |
                  v
       Entity & Relationship Extraction
                  |
                  v
       Data Cleaning & Normalization
                  |
                  v
          Neo4j AuraDB Graph
                  |
                  v
          User Question
                  |
                  v
        Question Classification
                  |
                  v
          Cypher Query Retrieval
                  |
                  v
       Retrieved Graph Context
          + PDF Evidence
                  |
                  v
        OpenAI GPT-4.1-mini
                  |
                  v
        AI Generated Answer
                  |
                  v
         Streamlit Chatbot
```

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| LangChain | LLM integration and application workflow |
| OpenAI GPT-4.1-mini | Question classification and answer generation |
| Neo4j AuraDB | Knowledge Graph database |
| Cypher | Graph query language |
| Streamlit | Interactive chatbot interface |
| PyPDF | PDF text extraction |
| python-dotenv | Environment variable management |

## 5. Knowledge Graph Information

The Knowledge Graph contains technical entities and their relationships extracted from the Micropilot FMR51 manual.

**Database verification:**
- Total nodes: 78
- Total relationships: 45
- Unique relationship types: 13

**Important relationship types:**
- `MANUFACTURED_BY`
- `HAS_MEASUREMENT_RANGE`
- `HAS_ACCURACY`
- `HAS_PROCESS_TEMPERATURE`
- `HAS_PROCESS_PRESSURE`
- `HAS_WETTED_MATERIAL`
- `HAS_CERTIFICATION`
- `HAS_OPTION`
- `HAS_PROCESS_CONNECTION`
- `SUPPORTS_APPLICATION`
- `SUPPORTS_COMMUNICATION`
- `USES_TECHNOLOGY`
- `MEASURES`

## 6. Example Technical Information

| Parameter | FMR51 Specification |
|---|---|
| Manufacturer | Endress+Hauser |
| Measurement range | 40 m standard |
| Advanced dynamics range | 70 m |
| Accuracy | ±2 mm |
| Maximum HT process temperature | +450 °C |
| Maximum XT process temperature | +280 °C |
| Maximum process pressure | 160 bar |
| Radar frequency | K-band, approximately 26 GHz |

Specifications are retrieved from the technical manual through the Knowledge Graph.

## 7. Application Features

1. Interactive technical question-answering chatbot.
2. Automatic question classification.
3. Neo4j Knowledge Graph retrieval.
4. Executed Cypher query visibility.
5. Retrieved graph records and relationship information.
6. Supporting PDF evidence.
7. PDF page references.
8. AI-generated technical responses.

## 8. Installation and Setup

### Prerequisites

- Python 3.13
- Neo4j AuraDB account
- OpenAI API key
- Visual Studio Code

### Clone the repository

```bash
git clone https://github.com/raj230987-star/Marine_KG_RAG_W3D1.git
cd Marine_KG_RAG
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment (Windows)

```powershell
.\venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_connection_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

Use your own Neo4j AuraDB connection details. Never upload `.env` or API credentials to GitHub.

## 9. Run the Application

```bash
streamlit run app.py
```

Open the local Streamlit URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 10. Sample Questions

Try asking:

- Who is the manufacturer of FMR51?
- What is the measurement range of Micropilot FMR51?
- What is the accuracy of FMR51?
- What is the maximum process temperature?
- What is the maximum process pressure?
- Which communication protocols are supported?
- Explain all technical specifications of FMR51.

## 11. Testing and Validation

The application was tested successfully with the following examples:

| Test Question | Expected Result |
|---|---|
| Manufacturer | Endress+Hauser |
| Measurement range | 40 m standard / 70 m Advanced dynamics |
| Accuracy | ±2 mm |
| Process temperature | HT up to +450 °C |
| Graph retrieval | Relevant records from Neo4j |
| Source evidence | PDF evidence and page references |

## 12. Future Enhancements

- Support multiple marine sensor PDF manuals.
- Add additional sensor manufacturers.
- Build a unified marine instrumentation Knowledge Graph.
- Include sensor comparison and specification analysis.
- Integrate real-time marine sensor data.
- Develop a web-based technical documentation assistant.

## 13. Author

**Project:** Marine Sensor KG-RAG Assistant  
**Domain:** Marine Instrumentation and AI-based Technical Documentation  
**Organization:** NTCPWC – IIT Madras

---

*Developed as a practical application of Generative AI, Knowledge Graphs and Retrieval-Augmented Generation for marine instrumentation documentation.*