
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "normalized_relationships.json"

with open(file_path, encoding="utf-8") as f:
    relationships = json.load(f)

fixed_count = 0

for rel in relationships:
    if rel["target_entity"].strip().lower() == "liquid level measurement":
        rel["target_entity"] = "Liquid level measurement"
        fixed_count += 1

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(relationships, f, indent=4, ensure_ascii=False)

print("Relationship name correction completed.")
print("Records corrected:", fixed_count)
