
from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal

# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([
    OPENAI_API_KEY,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
]):
    raise ValueError("Missing credentials. Check your .env file.")

# --------------------------------------------------
# 2. INITIALIZE OPENAI MODEL
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

# --------------------------------------------------
# 3. DEFINE QUESTION CATEGORIES
# --------------------------------------------------

class QuestionIntent(BaseModel):

    category: Literal[
        "manufacturer",
        "accuracy",
        "measurement_range",
        "process_temperature",
        "process_pressure",
        "communication",
        "technology",
        "application",
        "all",
        "unknown"
    ] = Field(description="Requested technical information")


intent_llm = llm.with_structured_output(QuestionIntent)

# --------------------------------------------------
# 4. NEO4J CONNECTION
# --------------------------------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# --------------------------------------------------
# 5. RELATIONSHIP MAPPING
# --------------------------------------------------

RELATIONSHIP_MAP = {
    "manufacturer": "MANUFACTURED_BY",
    "accuracy": "HAS_ACCURACY",
    "measurement_range": "HAS_MEASUREMENT_RANGE",
    "process_temperature": "HAS_PROCESS_TEMPERATURE",
    "process_pressure": "HAS_PROCESS_PRESSURE",
    "communication": "SUPPORTS_COMMUNICATION",
    "technology": "USES_TECHNOLOGY",
    "application": "SUPPORTS_APPLICATION"
}

# --------------------------------------------------
# 6. RETRIEVE DATA AND SOURCE EVIDENCE FROM NEO4J
# --------------------------------------------------

def retrieve_graph_data(sensor_name, category):

    with driver.session() as session:

        if category == "all":

            query = """
            MATCH (source:Entity {name: $sensor_name})
                  -[r]->(target:Entity)

            RETURN
                type(r) AS relationship,
                target.name AS information,
                r.evidence AS evidence,
                r.page_number AS page_number

            ORDER BY relationship
            """

            result = session.run(
                query,
                sensor_name=sensor_name
            )

        elif category in RELATIONSHIP_MAP:

            query = """
            MATCH (source:Entity {name: $sensor_name})
                  -[r]->(target:Entity)

            WHERE type(r) = $relationship

            RETURN
                type(r) AS relationship,
                target.name AS information,
                r.evidence AS evidence,
                r.page_number AS page_number
            """

            result = session.run(
                query,
                sensor_name=sensor_name,
                relationship=RELATIONSHIP_MAP[category]
            )

        else:
            return []

        return [dict(record) for record in result]


# --------------------------------------------------
# 7. GENERATE ANSWER USING OPENAI
# --------------------------------------------------

def generate_answer(question, graph_data):

    if not graph_data:
        return (
            "No supporting information was found "
            "in the knowledge graph."
        )

    prompt = f"""
You are a Marine Instrumentation Technical Assistant.

Answer the user's question using ONLY the supplied
Neo4j knowledge graph information.

Rules:
1. Do not invent technical specifications.
2. Do not use outside information.
3. If information is missing, say so.
4. Give a clear and concise technical answer.
5. Do not invent source page numbers.

USER QUESTION:
{question}

KNOWLEDGE GRAPH DATA:
{graph_data}

Provide the technical answer.
"""

    response = llm.invoke(prompt)

    return response.content


# --------------------------------------------------
# 8. DISPLAY SOURCE REFERENCES
# --------------------------------------------------

def display_sources(graph_data):

    print("\nSOURCE REFERENCES")
    print("=" * 55)

    seen = set()

    for item in graph_data:

        evidence = item.get("evidence")
        page_number = item.get("page_number")

        source_key = (evidence, page_number)

        if source_key in seen:
            continue

        seen.add(source_key)

        print("\nRelationship:", item["relationship"])
        print("Information:", item["information"])

        if evidence:
            print("Evidence:", evidence)
        else:
            print("Evidence: Not available")

        if page_number is not None:
            print("PDF Page Number:", page_number)
        else:
            print("PDF Page Number: Not available")


# --------------------------------------------------
# 9. QUESTION ANSWERING FUNCTION
# --------------------------------------------------

def ask_question(question):

    sensor_name = "Micropilot FMR51"

    print("\nUnderstanding question...")

    intent = intent_llm.invoke(
        f"""
Identify the technical information category
requested in this question about Micropilot FMR51.

Question: {question}

Available categories:
manufacturer, accuracy, measurement_range,
process_temperature, process_pressure,
communication, technology, application,
all, unknown.

Choose all for general sensor information.
Choose unknown if no category matches.
"""
    )

    print("Detected category:", intent.category)

    print("\nSearching Neo4j knowledge graph...")

    graph_data = retrieve_graph_data(
        sensor_name,
        intent.category
    )

    print("Graph records retrieved:", len(graph_data))

    print("\nAI GENERATED ANSWER")
    print("=" * 55)

    answer = generate_answer(question, graph_data)

    print(answer)

    display_sources(graph_data)


# --------------------------------------------------
# 10. MAIN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    try:

        driver.verify_connectivity()

        print("Neo4j connected successfully!")
        print("Marine Sensor KG-RAG Assistant")
        print("=" * 55)

        while True:

            question = input(
                "\nAsk your question (type exit to close): "
            ).strip()

            if question.lower() in ["exit", "quit"]:
                break

            if not question:
                print("Please enter a question.")
                continue

            try:
                ask_question(question)

            except Exception as error:
                print("\nQuestion processing error:", error)

    except Exception as error:

        print("\nConnection error:", error)

    finally:

        driver.close()
        print("\nNeo4j connection closed.")
