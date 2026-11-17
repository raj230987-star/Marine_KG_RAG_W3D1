
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI


# ==========================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# STEP 2: DEFINE ENTITY DATA STRUCTURE
# ==========================================

class Entity(BaseModel):
    name: str = Field(description="Name of the extracted entity")

    entity_type: str = Field(
        description="Category such as Sensor, Manufacturer, Technology, "
                    "Application, Measurement_Range, Accuracy or Output_Signal"
    )

    description: str = Field(
        description="Brief explanation based only on the document"
    )

    evidence: str = Field(
        description="Exact supporting text from the PDF"
    )


class EntityExtraction(BaseModel):
    entities: List[Entity] = Field(
        description="List of entities extracted from the document page"
    )


# ==========================================
# STEP 3: LOAD PDF DOCUMENT
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

pdf_path = BASE_DIR / "documents" / "FMR51_manual.pdf"

loader = PyPDFLoader(str(pdf_path))

documents = loader.load()

print("PDF Loaded Successfully!")
print("Total Pages:", len(documents))


# ==========================================
# STEP 4: INITIALIZE OPENAI LLM
# ==========================================

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

extractor = llm.with_structured_output(EntityExtraction)


# ==========================================
# STEP 5: DEFINE EXTRACTION PROMPT
# ==========================================

system_prompt = """
You are a technical knowledge extraction assistant.

Extract important technical entities from the supplied
marine instrumentation document.

Identify entities such as:

1. Sensor
2. Manufacturer
3. Technology
4. Application
5. Measurement Parameter
6. Measurement Range
7. Accuracy
8. Output Signal
9. Process Temperature
10. Process Pressure
11. Wetted Materials

Rules:

- Extract only information explicitly supported by the text.
- Do not invent missing specifications.
- Preserve technical values and units.
- Include a short supporting evidence quotation.
- If no useful entities are found, return an empty list.
"""


# ==========================================
# STEP 6: EXTRACT ENTITIES PAGE BY PAGE
# ==========================================

all_entities = []

for page_index, document in enumerate(documents):

    page_number = page_index + 1

    page_text = document.page_content

    if not page_text.strip():
        continue

    print(f"\nProcessing Page {page_number}...")

    result = extractor.invoke([
        ("system", system_prompt),
        (
            "human",
            f"""
            Extract entities from this PDF page.

            Page Number: {page_number}

            Document Text:
            {page_text}
            """
        )
    ])

    # Add page number to each entity record
    for entity in result.entities:

        entity_data = entity.model_dump()

        entity_data["page_number"] = page_number

        all_entities.append(entity_data)


# ==========================================
# STEP 7: DISPLAY EXTRACTED ENTITIES
# ==========================================

print("\n========== EXTRACTED ENTITIES ==========")

for entity in all_entities:

    print("\nEntity Name:", entity["name"])
    print("Entity Type:", entity["entity_type"])
    print("Description:", entity["description"])
    print("Evidence:", entity["evidence"])
    print("Page Number:", entity["page_number"])


# ==========================================
# STEP 8: SAVE ENTITIES AS JSON
# ==========================================

import json

output_path = BASE_DIR / "entities.json"

with open(output_path, "w", encoding="utf-8") as file:

    json.dump(
        all_entities,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n======================================")
print("ENTITY EXTRACTION COMPLETED!")
print("Total Entities:", len(all_entities))
print("Saved File:", output_path)
print("======================================")
