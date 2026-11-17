
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

# STEP 1: Define PDF path
pdf_path = Path("documents/FMR51_manual.pdf")

# STEP 2: Check PDF availability
if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

print("PDF found successfully!")

# STEP 3: Initialize PDF loader
loader = PyPDFLoader(str(pdf_path))

# STEP 4: Load PDF document
documents = loader.load()

# STEP 5: Display total pages
print("\n========== DOCUMENT INFORMATION ==========")
print("PDF File:", pdf_path.name)
print("Total Pages:", len(documents))

# STEP 6: Display first page text
print("\n========== FIRST PAGE CONTENT ==========")
print(documents[0].page_content[:1500])

# STEP 7: Display metadata
print("\n========== DOCUMENT METADATA ==========")
print(documents[0].metadata)

print("\nPDF LOADED SUCCESSFULLY!")


print("\n========== ALL PAGE INFORMATION ==========")

for index, doc in enumerate(documents):

    print(f"\nPage Number: {index + 1}")

    print("Text Length:", len(doc.page_content))

    print("Metadata:", doc.metadata)
