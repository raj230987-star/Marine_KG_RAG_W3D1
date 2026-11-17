
import json
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI


# ==================================================
# 1. PROJECT PATHS AND ENVIRONMENT
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

# Load OpenAI API key from .env
load_dotenv(BASE_DIR / ".env")

PDF_PATH = BASE_DIR / "documents" / "FMR51_manual.pdf"
OUTPUT_PATH = BASE_DIR / "relationships.json"


# ==================================================
# 2. CHECK API KEY
# ==================================================

import os

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not found. Please check your .env file."
    )


# ==================================================
# 3. RELATIONSHIP DATA STRUCTURE
# ==================================================

class Relationship(BaseModel):
    source_entity: str = Field(
        description="Source entity name"
    )

    relationship: str = Field(
        description="Relationship type"
    )

    target_entity: str = Field(
        description="Target entity name or value"
    )

    evidence: str = Field(
        description="Supporting evidence from PDF"
    )


class RelationshipExtraction(BaseModel):
    relationships: List[Relationship]


# ==================================================
# 4. ALLOWED RELATIONSHIP TYPES
# ==================================================

ALLOWED_RELATIONSHIPS = [
    "MANUFACTURED_BY",
    "USES_TECHNOLOGY",
    "MEASURES",
    "HAS_ACCURACY",
    "HAS_MEASUREMENT_RANGE",
    "SUPPORTS_OUTPUT",
    "HAS_PROCESS_TEMPERATURE",
    "HAS_PROCESS_PRESSURE",
    "HAS_WETTED_MATERIAL",
    "OPERATES_AT_FREQUENCY",
    "HAS_CERTIFICATION",
    "HAS_OPTION",
    "HAS_PROCESS_CONNECTION",
    "SUPPORTS_APPLICATION"
]


# ==================================================
# 5. LOAD PDF DOCUMENT
# ==================================================

if not PDF_PATH.exists():
    raise FileNotFoundError(
        f"PDF file not found: {PDF_PATH}"
    )

loader = PyPDFLoader(str(PDF_PATH))
documents = loader.load()

print("PDF loaded successfully.")
print(f"Total pages: {len(documents)}")


# ==================================================
# 6. CONFIGURE OPENAI MODEL
# ==================================================

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

relationship_extractor = llm.with_structured_output(
    RelationshipExtraction
)


# ==================================================
# 7. EXTRACT RELATIONSHIPS PAGE BY PAGE
# ==================================================

all_relationships = []

for index, document in enumerate(documents):

    page_number = index + 1
    page_text = document.page_content.strip()

    if not page_text:
        print(f"Page {page_number}: No text found.")
        continue

    print(f"\nProcessing page {page_number}...")

    prompt = f"""
You are a technical knowledge graph engineer.

Analyze this page from the Endress+Hauser
Micropilot FMR51 technical manual.

Extract only technically valid relationships.

IMPORTANT RULES:

1. Use only information explicitly mentioned on this page.
2. Every relationship must have supporting evidence.
3. Never invent technical specifications.
4. Never infer missing information.
5. Use only these relationship types:

{ALLOWED_RELATIONSHIPS}

6. Use Micropilot FMR51 as the source only when
   the specification explicitly belongs to FMR51.
7. Do not associate specifications belonging to
   FMR50, FMR52, FMR53 or FMR54 with FMR51.
8. Do not create relationships from assumptions.
9. Do not return relationships with missing evidence.
10. If no valid relationships exist, return an empty list.

Examples:

Source: Micropilot FMR51
Relationship: MANUFACTURED_BY
Target: Endress+Hauser

Source: Micropilot FMR51
Relationship: HAS_ACCURACY
Target: ±2 mm

Source: Micropilot FMR51
Relationship: SUPPORTS_OUTPUT
Target: 4–20 mA HART

Return structured relationship data.

PAGE NUMBER: {page_number}

PDF CONTENT:
{page_text}
"""

    try:

        result = relationship_extractor.invoke(prompt)

        page_count = 0

        for relationship in result.relationships:

            relationship_type = relationship.relationship.upper().strip()

            # Validate relationship type
            if relationship_type not in ALLOWED_RELATIONSHIPS:
                continue

            # Validate evidence
            if not relationship.evidence.strip():
                continue

            # Validate source and target
            if not relationship.source_entity.strip():
                continue

            if not relationship.target_entity.strip():
                continue

            record = relationship.model_dump()

            record["relationship"] = relationship_type
            record["page_number"] = page_number

            all_relationships.append(record)
            page_count += 1

        print(
            f"Page {page_number}: "
            f"{page_count} valid relationships extracted."
        )

    except Exception as error:

        print(
            f"Error processing page {page_number}: {error}"
        )


# ==================================================
# 8. REMOVE EXACT DUPLICATES
# ==================================================

unique_relationships = []
seen = set()

for item in all_relationships:

    key = (
        item["source_entity"].strip().lower(),
        item["relationship"],
        item["target_entity"].strip().lower(),
        item["evidence"].strip().lower()
    )

    if key not in seen:

        seen.add(key)
        unique_relationships.append(item)


# ==================================================
# 9. SAVE JSON FILE
# ==================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        unique_relationships,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# 10. DISPLAY RESULTS
# ==================================================

print("\n======================================")
print("RELATIONSHIP EXTRACTION COMPLETED")
print("======================================")

print(
    f"Total relationships: {len(unique_relationships)}"
)

print(f"Saved file: {OUTPUT_PATH}")

print("\nSample relationships:\n")

for item in unique_relationships[:15]:

    print(
        f'{item["source_entity"]} '
        f'--[{item["relationship"]}]--> '
        f'{item["target_entity"]}'
    )

print("\n======================================")
print("PROCESS FINISHED")
print("======================================")
