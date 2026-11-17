
from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("Neo4j credentials missing. Check your .env file.")

# --------------------------------------------------
# 2. CONNECT TO NEO4J
# --------------------------------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# --------------------------------------------------
# 3. GRAPH QUERY FUNCTION
# --------------------------------------------------

def get_sensor_information(sensor_name):

    query = """
    MATCH (source:Entity {name: $sensor_name})
          -[r]->(target:Entity)

    RETURN
        type(r) AS relationship,
        target.name AS information

    ORDER BY relationship
    """

    with driver.session() as session:

        results = session.run(
            query,
            sensor_name=sensor_name
        )

        records = list(results)

        if not records:
            print("No information found for:", sensor_name)
            return

        for record in records:
            print(
                f"{record['relationship']}: "
                f"{record['information']}"
            )


# --------------------------------------------------
# 4. QUERY SPECIFIC TECHNICAL PARAMETER
# --------------------------------------------------

def get_measurement_range(sensor_name):

    query = """
    MATCH (source:Entity {name: $sensor_name})
          -[:HAS_MEASUREMENT_RANGE]->(target:Entity)

    RETURN target.name AS measurement_range
    """

    with driver.session() as session:

        results = session.run(
            query,
            sensor_name=sensor_name
        )

        records = list(results)

        print("\nMEASUREMENT RANGE")
        print("-" * 50)

        if not records:
            print("Measurement range not found.")
            return

        for record in records:
            print("Measurement Range:", record["measurement_range"])


# --------------------------------------------------
# 5. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    try:

        driver.verify_connectivity()

        print("Connected to Neo4j successfully!")

        sensor_name = "Micropilot FMR51"

        print("\nMARINE SENSOR KNOWLEDGE GRAPH")
        print("=" * 55)
        print("Sensor:", sensor_name)

        print("\nALL SENSOR INFORMATION")
        print("-" * 50)

        get_sensor_information(sensor_name)

        get_measurement_range(sensor_name)

    except Exception as error:

        print("\nError:", error)

    finally:

        driver.close()
        print("\nNeo4j connection closed.")
