
import os
import ssl
from pathlib import Path
from typing import Literal

import certifi
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Marine Sensor KG-RAG",
    page_icon="🌊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# ==================================================
# 2. OPENAI LLM CONFIGURATION
# ==================================================

@st.cache_resource
def get_llm():

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in .env")

    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )


llm = get_llm()


# ==================================================
# 3. QUESTION CLASSIFICATION
# ==================================================

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


# ==================================================
# 4. CATEGORY TO NEO4J RELATIONSHIP MAPPING
# ==================================================

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


# ==================================================
# 5. NEO4J CONNECTION WITH SSL FIX
# ==================================================

@st.cache_resource
def get_neo4j_driver():

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError(
            "Neo4j credentials are missing in .env"
        )

    # Use trusted CA certificates
    os.environ["SSL_CERT_FILE"] = certifi.where()

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    # Convert secure routing URI to standard URI
    # and explicitly configure encrypted connection
    secure_uri = uri.replace(
        "neo4j+s://",
        "neo4j://"
    )

    driver = GraphDatabase.driver(
        secure_uri,
        auth=(username, password),
        encrypted=True,
        ssl_context=ssl_context
    )

    # Verify Neo4j connection
    driver.verify_connectivity()

    return driver


# ==================================================
# 6. QUESTION CLASSIFICATION FUNCTION
# ==================================================

def classify_question(question):

    prompt = f"""
    You are a question classification assistant.

    Classify the user's question about the
    Endress+Hauser Micropilot FMR51 sensor.

    Available categories:

    manufacturer
    accuracy
    measurement_range
    process_temperature
    process_pressure
    communication
    technology
    application
    all
    unknown

    Classification rules:

    Manufacturer questions -> manufacturer

    Accuracy questions -> accuracy

    Measuring distance or range -> measurement_range

    Temperature questions -> process_temperature

    Pressure questions -> process_pressure

    Communication questions -> communication

    Radar or measurement principle -> technology

    Application questions -> application

    All specification questions -> all

    Unrelated questions -> unknown

    User Question:
    {question}
    """

    result = intent_llm.invoke(prompt)

    return result.category


# ==================================================
# 7. NEO4J KNOWLEDGE GRAPH RETRIEVAL
# ==================================================

def retrieve_graph_data(category):

    driver = get_neo4j_driver()

    if category == "all":

        query = """
        MATCH (source:Entity {name: "Micropilot FMR51"})
              -[r]->(target:Entity)

        RETURN
            type(r) AS relationship,
            target.name AS information,
            r.evidence AS evidence,
            r.page_number AS page_number

        ORDER BY relationship
        """

        parameters = {}

    else:

        relationship_types = CATEGORY_RELATIONSHIPS.get(
            category, []
        )

        if not relationship_types:
            return [], None

        query = """
        MATCH (source:Entity {name: "Micropilot FMR51"})
              -[r]->(target:Entity)

        WHERE type(r) IN $relationship_types

        RETURN
            type(r) AS relationship,
            target.name AS information,
            r.evidence AS evidence,
            r.page_number AS page_number

        ORDER BY relationship
        """

        parameters = {
            "relationship_types": relationship_types
        }

    with driver.session() as session:

        result = session.run(
            query,
            parameters
        )

        graph_data = [
            record.data()
            for record in result
        ]

    return graph_data, query


# ==================================================
# 8. LLM ANSWER GENERATION
# ==================================================

def generate_answer(question, graph_data):

    if not graph_data:

        return (
            "I could not find supporting information "
            "for this question in the Marine Sensor "
            "Knowledge Graph. Please ask a question "
            "related to Micropilot FMR51 specifications."
        )

    prompt = f"""
    You are a Marine Instrumentation Technical Assistant.

    Answer the user's question using ONLY the
    retrieved Neo4j Knowledge Graph information.

    Rules:

    1. Do not invent technical specifications.
    2. Do not use outside information.
    3. Use only the retrieved graph context.
    4. If information is unavailable, mention it.
    5. Give a clear and technically accurate answer.
    6. Include units wherever available.

    USER QUESTION:

    {question}

    RETRIEVED KNOWLEDGE GRAPH CONTEXT:

    {graph_data}

    Generate the final technical answer.
    """

    response = llm.invoke(prompt)

    return response.content


# ==================================================
# 9. COMPLETE KG-RAG PIPELINE
# ==================================================

def answer_question(question):

    # Step 1: Classify user question
    category = classify_question(question)

    # Step 2: Retrieve information from Neo4j
    graph_data, cypher_query = retrieve_graph_data(
        category
    )

    # Step 3: Generate answer using retrieved context
    answer = generate_answer(
        question,
        graph_data
    )

    return {
        "answer": answer,
        "category": category,
        "graph_data": graph_data,
        "cypher_query": cypher_query
    }


# ==================================================
# 10. DISPLAY RETRIEVED GRAPH CONTEXT
# ==================================================

def display_graph_sources(graph_data):

    if not graph_data:

        st.warning(
            "No supporting records were retrieved from Neo4j."
        )

        return

    st.success(
        f"Retrieved {len(graph_data)} knowledge graph "
        "record(s) from Neo4j."
    )

    for index, source in enumerate(graph_data, start=1):

        st.markdown(f"#### Retrieved Record {index}")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"**Relationship:** "
                f"`{source.get('relationship') or 'N/A'}`"
            )

            st.markdown(
                f"**Information:** "
                f"{source.get('information') or 'N/A'}"
            )

        with col2:

            page = source.get("page_number")

            st.markdown(
                f"**PDF Page:** "
                f"{page if page is not None else 'Not available'}"
            )

        st.markdown("**Supporting PDF Evidence:**")

        st.info(
            source.get("evidence") or "Evidence not available"
        )

        st.divider()


# ==================================================
# 11. DISPLAY CHAT HISTORY
# ==================================================

def display_message(message):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            category = message.get("category")

            if category:

                st.caption(
                    f"Detected category: {category}"
                )

            sources = message.get("sources", [])

            if sources:

                with st.expander(
                    "🔍 Retrieved Knowledge Graph Context & PDF Sources"
                ):

                    display_graph_sources(sources)

            cypher_query = message.get("cypher_query")

            if cypher_query:

                with st.expander(
                    "🗄️ View Neo4j Cypher Query"
                ):

                    st.code(
                        cypher_query,
                        language="cypher"
                    )


# ==================================================
# 12. MAIN APPLICATION INTERFACE
# ==================================================

st.title("🌊 Marine Sensor KG-RAG Assistant")

st.subheader(
    "Knowledge Graph Retrieval-Augmented Generation"
)

st.markdown(
    """
    Ask technical questions about the
    **Endress+Hauser Micropilot FMR51 Radar Level Sensor**.

    This chatbot retrieves technical information from
    a Neo4j Knowledge Graph and generates answers
    using OpenAI GPT-4.1-mini.
    """
)


# ==================================================
# 13. SIDEBAR
# ==================================================

with st.sidebar:

    st.header("📘 Project Information")

    st.write("**Project:** Marine Sensor KG-RAG")

    st.write("**Document:** FMR51 Technical Manual")

    st.write("**Knowledge Graph:** Neo4j AuraDB")

    st.write("**LLM:** OpenAI GPT-4.1-mini")

    st.write("**Framework:** LangChain")

    st.divider()

    st.subheader("⚙️ KG-RAG Workflow")

    st.write("1. User Question")

    st.write("2. Question Classification")

    st.write("3. Neo4j Graph Retrieval")

    st.write("4. Retrieved Context")

    st.write("5. LLM Answer Generation")

    st.write("6. PDF Source References")

    st.divider()

    if st.button(
        "🗑️ Clear Chat History",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ==================================================
# 14. INITIALIZE CHAT HISTORY
# ==================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    display_message(message)


# ==================================================
# 15. CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask about FMR51 measurement range, accuracy, "
    "temperature, pressure or communication..."
)


if question:

    # Display user question

    st.session_state.messages.append({

        "role": "user",
        "content": question

    })

    with st.chat_message("user"):

        st.markdown(question)


    # Generate response

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Classifying question and retrieving "
                "knowledge from Neo4j..."
            ):

                result = answer_question(question)

            answer = result["answer"]

            category = result["category"]

            graph_data = result["graph_data"]

            cypher_query = result["cypher_query"]


            # Display final AI answer

            st.markdown("### 🤖 AI Generated Answer")

            st.markdown(answer)


            # Display classification

            st.markdown("### 🧠 Question Classification")

            st.info(
                f"Detected Category: {category}"
            )


            # Display graph retrieval status

            st.markdown(
                "### 🔗 Knowledge Graph Retrieval"
            )

            if graph_data:

                st.success(
                    f"Successfully retrieved "
                    f"{len(graph_data)} graph record(s) "
                    "from Neo4j."
                )

            else:

                st.warning(
                    "No matching graph records found."
                )


            # Display executed Cypher query

            if cypher_query:

                with st.expander(
                    "🗄️ View Executed Neo4j Cypher Query"
                ):

                    st.code(
                        cypher_query,
                        language="cypher"
                    )


            # Display retrieved context and PDF sources

            with st.expander(
                "📚 Retrieved Context & PDF Source Evidence",
                expanded=True
            ):

                display_graph_sources(graph_data)


            # Save assistant response

            st.session_state.messages.append({

                "role": "assistant",

                "content": answer,

                "category": category,

                "sources": graph_data,

                "cypher_query": cypher_query

            })


        except Exception as error:

            st.error(
                f"An error occurred: {error}"
            )

            st.info(
                "Check your OpenAI API key, Neo4j "
                "connection and .env configuration."
            )


# ==================================================
# 16. FOOTER
# ==================================================

st.divider()

st.caption(
    "Marine Sensor KG-RAG | Python | LangChain | "
    "Neo4j AuraDB | OpenAI GPT-4.1-mini | Streamlit"
)
