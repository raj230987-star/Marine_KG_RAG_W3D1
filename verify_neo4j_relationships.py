
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

with open(BASE_DIR / "normalized_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

try:
    with driver.session() as session:

        print("\nNEO4J RELATIONSHIP VERIFICATION")
        print("-" * 50)

        missing = []

        for rel in relationships:
            result = session.run("""
                MATCH (s:Entity {name: $source})
                      -[r]-> 
                      (t:Entity {name: $target})
                WHERE type(r) = $relationship
                RETURN count(r) AS total
            """,
                source=rel["source_entity"].strip(),
                target=rel["target_entity"].strip(),
                relationship=rel["relationship"]
            )

            count = result.single()["total"]

            if count == 0:
                missing.append(rel)

        if missing:
            print("Relationships not found:", len(missing))

            for rel in missing:
                print("\nSource:", rel["source_entity"])
                print("Type:", rel["relationship"])
                print("Target:", rel["target_entity"])
        else:
            print("All relationship combinations found in Neo4j.")

finally:
    driver.close()
