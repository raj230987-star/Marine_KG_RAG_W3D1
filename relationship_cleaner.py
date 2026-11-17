
import json
from pathlib import Path


# ==================================================
# 1. FILE PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "relationships.json"

OUTPUT_FILE = BASE_DIR / "cleaned_relationships.json"

REVIEW_FILE = BASE_DIR / "relationships_review.json"


# ==================================================
# 2. RELATIONSHIP TYPE MAPPING
# ==================================================

RELATIONSHIP_MAPPING = {

    "SUPPORTS_OUTPUT": "SUPPORTS_COMMUNICATION",

}


# ==================================================
# 3. RELATIONSHIPS TO REMOVE
# ==================================================

# These records have weak or insufficient evidence.
REMOVE_RULES = [

    {
        "page": 1,
        "relationship": "MANUFACTURED_BY",
        "target": "Endress+Hauser",
        "reason": "Manufacturer inferred only from website URL."
    },

    {
        "page": 2,
        "relationship": "USES_TECHNOLOGY",
        "target": "innovative and patented sensor-design",
        "reason": "Vague description, not a specific technology."
    }

]


# ==================================================
# 4. RELATIONSHIPS THAT NEED REVIEW
# ==================================================

REVIEW_RULES = [

    {
        "page": 2,
        "target": "Horn antenna: 40...100 mm",
        "reason": "This appears to describe antenna dimensions, not process connection."
    },

    {
        "page": 4,
        "target": "ASME B31.3",
        "reason": "Review as a design code rather than a certification."
    },

    {
        "page": 4,
        "target": "NACE MR0175, MR0103",
        "reason": "Review as material/design compliance requirements."
    },

    {
        "page": 4,
        "target": "EN 10204-3.1",
        "reason": "Material inspection documentation; not necessarily a certification."
    },

    {
        "page": 5,
        "target": "Endress+Hauser (India) Pvt. Ltd.",
        "reason": "Confirm whether this is the manufacturer or regional contact."
    },

    {
        "page": 4,
        "target": "GL/ ABS/ LR/ BV/ DNV",
        "reason": "Confirm individual marine approvals and applicability to FMR51."
    }

]


# ==================================================
# 5. LOAD ORIGINAL JSON
# ==================================================

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

with open(INPUT_FILE, "r", encoding="utf-8") as file:

    relationships = json.load(file)

print("Original relationship file loaded.")
print("Total original relationships:", len(relationships))


# ==================================================
# 6. VALIDATION AND CLEANING
# ==================================================

cleaned_relationships = []

review_relationships = []

removed_count = 0

for item in relationships:

    source = item.get("source_entity", "").strip()

    relation = item.get("relationship", "").strip().upper()

    target = item.get("target_entity", "").strip()

    evidence = item.get("evidence", "").strip()

    page = item.get("page_number")

    # ----------------------------------------------
    # Check missing information
    # ----------------------------------------------

    if not source or not relation or not target or not evidence:

        review_relationships.append({
            "record": item,
            "reason": "Missing source, relationship, target or evidence."
        })

        continue

    # ----------------------------------------------
    # Remove weak evidence
    # ----------------------------------------------

    should_remove = False

    for rule in REMOVE_RULES:

        if (
            page == rule["page"]
            and relation == rule["relationship"]
            and target.lower() == rule["target"].lower()
        ):

            should_remove = True

            print(
                f"REMOVED: {target} | {rule['reason']}"
            )

            removed_count += 1

            break

    if should_remove:
        continue

    # ----------------------------------------------
    # Check uncertain relationships
    # ----------------------------------------------

    needs_review = False

    for rule in REVIEW_RULES:

        if (
            page == rule["page"]
            and target.lower() == rule["target"].lower()
        ):

            review_relationships.append({
                "record": item,
                "reason": rule["reason"]
            })

            print(
                f"REVIEW: {target} | {rule['reason']}"
            )

            needs_review = True

            break

    # Do not automatically insert uncertain records.
    if needs_review:
        continue

    # ----------------------------------------------
    # Normalize relationship types
    # ----------------------------------------------

    if relation in RELATIONSHIP_MAPPING:

        new_relation = RELATIONSHIP_MAPPING[relation]

        item["relationship"] = new_relation

        print(
            f"UPDATED: {relation} -> {new_relation}"
        )

    # ----------------------------------------------
    # Normalize manufacturer name
    # ----------------------------------------------

    if (
        relation == "MANUFACTURED_BY"
        and target.lower() == "endress+hauser"
    ):

        item["target_entity"] = "Endress+Hauser"

    # ----------------------------------------------
    # Save validated relationship
    # ----------------------------------------------

    cleaned_relationships.append(item)


# ==================================================
# 7. REMOVE EXACT DUPLICATES
# ==================================================

unique_relationships = []

seen = set()

for item in cleaned_relationships:

    key = (
        item["source_entity"].lower().strip(),
        item["relationship"].upper().strip(),
        item["target_entity"].lower().strip()
    )

    if key not in seen:

        seen.add(key)

        unique_relationships.append(item)


# ==================================================
# 8. SAVE CLEANED RELATIONSHIPS
# ==================================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        unique_relationships,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# 9. SAVE REVIEW RECORDS
# ==================================================

with open(REVIEW_FILE, "w", encoding="utf-8") as file:

    json.dump(
        review_relationships,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# 10. DISPLAY SUMMARY
# ==================================================

print("\n======================================")
print("RELATIONSHIP CLEANING COMPLETED")
print("======================================")

print("Original relationships:", len(relationships))

print("Removed relationships:", removed_count)

print("Review required:", len(review_relationships))

print("Cleaned relationships:", len(unique_relationships))

print("\nOutput files:")

print("1.", OUTPUT_FILE.name)

print("2.", REVIEW_FILE.name)

print("\n======================================")
