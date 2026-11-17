
from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Find project folder
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Read Neo4j credentials
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Check credentials
if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("Neo4j credentials missing. Check your .env file.")

# Create database connection
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

try:
    # Verify database connection
    driver.verify_connectivity()

    print("Neo4j connection successful!")

    # Execute a test query
    with driver.session() as session:
        result = session.run(
            "RETURN 'Marine Sensor KG-RAG' AS project"
        )

        record = result.single()

        print("Connected Project:", record["project"])

finally:
    driver.close()
    print("Neo4j connection closed.")
