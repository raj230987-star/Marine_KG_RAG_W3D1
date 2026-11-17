
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "entities.json", encoding="utf-8") as f:
    entities = json.load(f)

with open(BASE_DIR / "cleaned_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

# Normalize a few known equivalent names
aliases = {
    "+/- 2 mm (0.08 in)": "±2 mm (0.08 in)",
    "Accuracy +/- 2 mm (0.08 in)": "±2 mm (0.08 in)",
    "XT: -196...+280 °C (-321...+536 °F)":
        "Process temperature XT: -196...+280 °C (-321...+536 °F)",
    "HT: -196...+450 °C (-321...+842 °F)":
        "Process temperature HT: -196...+450 °C (-321...+842 °F)",
}

for rel in relationships:
    rel["target_entity"] = aliases.get(
        rel["target_entity"],
        rel["target_entity"]
    )

# Correct known entity categories
for entity in entities:
    name = entity["name"].lower()

    if name.startswith("process connection"):
        entity["entity_type"] = "Process Connection"

    elif name == "40...100 mm":
        entity["entity_type"] = "Antenna Dimension"

    elif "ambient temperature" in name:
        entity["entity_type"] = "Ambient Temperature"

    elif "output_signal" in entity["entity_type"].lower():
        entity["entity_type"] = "Output Signal"

# Add missing relationship targets as technical-value nodes
existing_names = {
    entity["name"].strip().lower()
    for entity in entities
}

for rel in relationships:
    target = rel["target_entity"].strip()

    if target.lower() not in existing_names:
        entities.append({
            "name": target,
            "entity_type": "Technical Value",
            "description": "Extracted from a relationship in the FMR51 manual.",
            "evidence": rel.get("evidence", ""),
            "page_number": rel.get("page_number")
        })

        existing_names.add(target.lower())

# Save normalized data separately
with open(BASE_DIR / "normalized_entities.json", "w", encoding="utf-8") as f:
    json.dump(entities, f, indent=4, ensure_ascii=False)

with open(BASE_DIR / "normalized_relationships.json", "w", encoding="utf-8") as f:
    json.dump(relationships, f, indent=4, ensure_ascii=False)

print("Normalization completed!")
print("Original entities:", len(json.load(
    open(BASE_DIR / "entities.json", encoding="utf-8")
)))
print("Normalized entities:", len(entities))
print("Relationships:", len(relationships))
print("Files created:")
print("1. normalized_entities.json")
print("2. normalized_relationships.json")
