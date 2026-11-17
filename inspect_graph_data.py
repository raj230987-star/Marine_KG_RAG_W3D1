
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

# Load JSON files
with open(BASE_DIR / "entities.json", encoding="utf-8") as f:
    entities = json.load(f)

with open(BASE_DIR / "cleaned_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

# 1. Entity category count
entity_types = Counter(
    entity["entity_type"] for entity in entities
)

print("\nENTITY CATEGORY SUMMARY")
print("-" * 40)

for name, count in entity_types.items():
    print(f"{name}: {count}")

# 2. Relationship type count
relationship_types = Counter(
    rel["relationship"] for rel in relationships
)

print("\nRELATIONSHIP TYPE SUMMARY")
print("-" * 40)

for name, count in relationship_types.items():
    print(f"{name}: {count}")

# 3. Check missing entity references
entity_names = {
    entity["name"].strip().lower()
    for entity in entities
}

missing_entities = set()

for rel in relationships:
    source = rel["source_entity"].strip().lower()
    target = rel["target_entity"].strip().lower()

    if source not in entity_names:
        missing_entities.add(rel["source_entity"])

    if target not in entity_names:
        missing_entities.add(rel["target_entity"])

print("\nMISSING ENTITY CHECK")
print("-" * 40)

if missing_entities:
    for name in sorted(missing_entities):
        print("Missing:", name)
else:
    print("All relationship entities are present.")

print("\nTOTAL ENTITIES:", len(entities))
print("TOTAL RELATIONSHIPS:", len(relationships))
