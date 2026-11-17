
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "normalized_relationships.json", encoding="utf-8") as f:
    relationships = json.load(f)

# Identify duplicate source + relationship + target combinations
keys = [
    (
        r["source_entity"].strip(),
        r["relationship"].strip(),
        r["target_entity"].strip()
    )
    for r in relationships
]

counts = Counter(keys)

print("\nDUPLICATE RELATIONSHIP CHECK")
print("-" * 50)

duplicates = {
    key: count for key, count in counts.items()
    if count > 1
}

if duplicates:
    for (source, relation, target), count in duplicates.items():
        print(f"\nSource: {source}")
        print(f"Relationship: {relation}")
        print(f"Target: {target}")
        print(f"Occurrences: {count}")
else:
    print("No duplicate relationships found.")

print("\nTotal relationship records:", len(relationships))
print("Unique relationship combinations:", len(counts))
print("Duplicate records:", len(relationships) - len(counts))
