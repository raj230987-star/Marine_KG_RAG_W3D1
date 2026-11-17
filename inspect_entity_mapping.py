
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "entities.json", encoding="utf-8") as f:
    entities = json.load(f)

with open(BASE_DIR / "cleaned_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

print("\n========== ENTITY NAMES ==========")

for entity in entities:
    print(
        f"{entity['entity_type']} | "
        f"{entity['name']} | "
        f"Page {entity.get('page_number')}"
    )

print("\n========== RELATIONSHIP TARGETS ==========")

seen = set()

for rel in relationships:
    target = rel["target_entity"]

    if target not in seen:
        seen.add(target)
        print(
            f"{rel['relationship']} | "
            f"{target} | "
            f"Page {rel.get('page_number')}"
        )

print("\nUnique relationship targets:", len(seen))
