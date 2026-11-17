
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Marine Sensor KG-RAG",
    page_icon="🌊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# 2. LLM CONFIGURATION
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# --------------------------------------------------
# 3. QUESTION CLASSIFICATION
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
    ]


intent_llm = llm.with_structured_output(QuestionIntent)


# --------------------------------------------------
# 4. CATEGORY TO RELATIONSHIP MAPPING
# --------------------------------------------------

CATEGORY_RELATIONSHIPS = {
    "manufacturer": ["MANUFACTURED_BY"],
    "accuracy": ["HAS_ACCURACY"],
    "measurement_range": ["HAS_MEASUREMENT_RANGE"],
    "process_temperature": ["HAS_PROCESS_TEMPERATURE"],
    "process_pressure": ["HAS_PROCESS_PRESSURE"],
    "communication": [
        "SUPPORTS_COMMUNICATION",
        "SUPPORTS_OUTPUT"
    ],
    "technology": ["USES_TECHNOLOGY"],
    "application": [
        "MEASURES",
        "SUPPORTS_APPLICATION"
    ]
}


# --------------------------------------------------
# 5. NEO4J CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_neo4j_driver():

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError("Neo4j credentials are missing in .env")

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()

    return driver


# --------------------------------------------------
# 6. CLASSIFY USER QUESTION
# --------------------------------------------------

def classify_question(question):

    prompt = f"""
    Classify this question about the Micropilot FMR51 sensor.

    Question: {question}

    Select the most suitable category:
    manufacturer, accuracy, measurement_range,
    process_temperature, process_pressure,
    communication, technology, application,
    all, unknown.

    Use unknown if the question is unrelated
    or cannot be classified.
    """

    result = intent_llm.invoke(prompt)

    return result.category


# --------------------------------------------------
# 7. RETRIEVE INFORMATION FROM NEO4J
# --------------------------------------------------

def retrieve_graph_data(category):

    driver = get_neo4j_driver()

    if category == "all":

        query = """
        MATCH (source:Entity {name: "Micropilot FMR51"})
              -[r]->(target:Entity)
        RETURN type(r) AS relationship,
               target.name AS information,
               r.evidence AS evidence,
               r.page_number AS page_number
        """

        with driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    relationship_types = CATEGORY_RELATIONSHIPS.get(
        category, []
    )

    if not relationship_types:
        return []

    query = """
    MATCH (source:Entity {name: "Micropilot FMR51"})
          -[r]->(target:Entity)
    WHERE type(r) IN $relationship_types
    RETURN type(r) AS relationship,
           target.name AS information,
           r.evidence AS evidence,
           r.page_number AS page_number
    """

    with driver.session() as session:
        result = session.run(
            query,
            relationship_types=relationship_types
        )

        return [record.data() for record in result]


# --------------------------------------------------
# 8. GENERATE ANSWER
# --------------------------------------------------

def generate_answer(question, graph_data):

    if not graph_data:
        return (
            "No supporting information was found "
            "in the knowledge graph."
        )

    prompt = f"""
    You are a Marine Instrumentation Technical Assistant.

    Answer the user's question using ONLY the
    Neo4j knowledge graph information below.

    Do not invent specifications.
    Do not use outside information.
    If information is unavailable, clearly say so.

    User Question:
    {question}

    Knowledge Graph Data:
    {graph_data}

    Give a clear, concise technical answer.
    """

    response = llm.invoke(prompt)

    return response.content


# --------------------------------------------------
# 9. MAIN QUESTION ANSWERING FUNCTION
# --------------------------------------------------

def answer_question(question):

    category = classify_question(question)

    graph_data = retrieve_graph_data(category)

    answer = generate_answer(
        question,
        graph_data
    )

    return answer, category, graph_data


# --------------------------------------------------
# 10. STREAMLIT USER INTERFACE
# --------------------------------------------------

st.title("🌊 Marine Sensor KG-RAG Assistant")

st.caption(
    "Knowledge Graph Retrieval-Augmented Generation "
    "for Marine Instrumentation"
)

st.markdown(
    "Ask technical questions about the "
    "**Endress+Hauser Micropilot FMR51** sensor."
)

# Sidebar
with st.sidebar:

    st.header("Project Information")

    st.write("**Project:** Marine Sensor KG-RAG")

    st.write("**Knowledge Graph:** Neo4j AuraDB")

    st.write("**AI Model:** GPT-4.1-mini")

    st.write("**Document:** FMR51 Manual")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                with st.expander("📚 View Source References"):

                    for source in sources:

                        st.markdown(
                            f"**Relationship:** "
                            f"{source.get('relationship')}"
                        )

                        st.markdown(
                            f"**Information:** "
                            f"{source.get('information')}"
                        )

                        st.markdown(
                            f"**Evidence:** "
                            f"{source.get('evidence') or 'Not available'}"
                        )

                        st.markdown(
                            f"**PDF Page:** "
                            f"{source.get('page_number') or 'Not available'}"
                        )

                        st.divider()


# Chat input
question = st.chat_input(
    "Ask a technical question about Micropilot FMR51..."
)


if question:

    # Display user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner(
            "Searching knowledge graph and generating answer..."
        ):

            try:

                answer, category, graph_data = answer_question(
                    question
                )

                st.markdown(answer)

                st.caption(
                    f"Detected category: {category}"
                )

                if graph_data:

                    with st.expander(
                        "📚 View Source References",
                        expanded=True
                    ):

                        for source in graph_data:

                            st.markdown(
                                f"**Relationship:** "
                                f"{source.get('relationship')}"
                            )

                            st.markdown(
                                f"**Information:** "
                                f"{source.get('information')}"
                            )

                            st.markdown(
                                f"**Evidence:** "
                                f"{source.get('evidence') or 'Not available'}"
                            )

                            st.markdown(
                                f"**PDF Page:** "
                                f"{source.get('page_number') or 'Not available'}"
                            )

                            st.divider()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": graph_data
                })

            except Exception as error:

                st.error(
                    f"An error occurred: {error}"
                )

                st.info(
                    "Check your Neo4j connection, "
                    "API key and .env configuration."
                )
