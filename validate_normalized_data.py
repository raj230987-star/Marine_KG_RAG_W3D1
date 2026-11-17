
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "normalized_entities.json", encoding="utf-8") as f:
    entities = json.load(f)

with open(BASE_DIR / "normalized_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

# Check entity references
entity_names = {
    entity["name"].strip().lower()
    for entity in entities
}

missing = []

for rel in relationships:
    source = rel["source_entity"].strip().lower()
    target = rel["target_entity"].strip().lower()

    if source not in entity_names:
        missing.append(("SOURCE", rel["source_entity"]))

    if target not in entity_names:
        missing.append(("TARGET", rel["target_entity"]))

print("\nNORMALIZED DATA VALIDATION")
print("-" * 40)
print("Total entities:", len(entities))
print("Total relationships:", len(relationships))
print("Unique entity names:", len(entity_names))

print("\nENTITY CATEGORY SUMMARY")
for category, count in Counter(
    e["entity_type"] for e in entities
).items():
    print(f"{category}: {count}")

print("\nMISSING REFERENCE CHECK")
if missing:
    for kind, name in missing:
        print(kind, "missing:", name)
else:
    print("SUCCESS: All relationship references are present.")

print("\nDUPLICATE ENTITY NAME CHECK")
duplicates = len(entities) - len(entity_names)
print("Duplicate records:", duplicates)
