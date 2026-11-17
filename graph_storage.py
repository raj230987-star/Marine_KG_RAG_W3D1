
import json
import os
import re
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Project directory
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Neo4j credentials
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([URI, USERNAME, PASSWORD]):
    raise ValueError("Check Neo4j credentials in .env")

# Load normalized JSON files
with open(BASE_DIR / "normalized_entities.json", encoding="utf-8") as f:
    entities = json.load(f)

with open(BASE_DIR / "normalized_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

# Consolidate duplicate entities
entity_map = {}

for entity in entities:
    name = entity["name"].strip()

    if name not in entity_map:
        entity_map[name] = {
            "name": name,
            "entity_type": entity["entity_type"],
            "description": entity.get("description", ""),
            "evidence": entity.get("evidence", ""),
            "pages": []
        }

    page = entity.get("page_number")

    if page is not None and page not in entity_map[name]["pages"]:
        entity_map[name]["pages"].append(page)

# Group relationships by type
grouped = defaultdict(list)

for rel in relationships:
    relation_type = rel["relationship"]

    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", relation_type):
        raise ValueError(f"Invalid relationship type: {relation_type}")

    grouped[relation_type].append(rel)

# Connect to Neo4j
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("Connected to Neo4j AuraDB!")

    with driver.session() as session:

        # Create unique constraint
        session.run("""
            CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
            FOR (e:Entity)
            REQUIRE e.name IS UNIQUE
        """)

        # Store entities
        for entity in entity_map.values():
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.entity_type = $entity_type,
                    e.description = $description,
                    e.evidence = $evidence,
                    e.pages = $pages
            """, **entity)

        print("Entities stored:", len(entity_map))

        # Store relationships
        for relation_type, records in grouped.items():

            query = f"""
                MATCH (source:Entity)
                MATCH (target:Entity)
                WHERE source.name = $source_name
                  AND target.name = $target_name
                MERGE (source)-[r:{relation_type}]->(target)
                SET r.evidence = $evidence,
                    r.page_number = $page_number
            """

            for rel in records:
                session.run(
                    query,
                    source_name=rel["source_entity"].strip(),
                    target_name=rel["target_entity"].strip(),
                    evidence=rel.get("evidence", ""),
                    page_number=rel.get("page_number")
                )

        print("Relationships stored:", len(relationships))

        # Verify graph
        result = session.run("""
            MATCH (e:Entity)
            RETURN count(e) AS node_count
        """)

        print("Neo4j node count:", result.single()["node_count"])

        result = session.run("""
            MATCH ()-[r]->()
            RETURN count(r) AS relationship_count
        """)

        print(
            "Neo4j relationship count:",
            result.single()["relationship_count"]
        )

finally:
    driver.close()
    print("Neo4j connection closed.")
