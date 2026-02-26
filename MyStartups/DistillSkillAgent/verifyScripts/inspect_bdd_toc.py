import sys
import os
from distillSkillAgent.parsers import PDFParser

pdf_path = "Books/BDD-in-Action.pdf"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    sys.exit(1)

print(f"Inspecting TOC for: {pdf_path}")
parser = PDFParser()
try:
    doc = parser.parse_pdf(pdf_path)
    print(f"Total Pages: {doc.metadata.get('page_count')}")
    print(f"TOC Found: {doc.metadata.get('toc_found')}")
    print(f"Number of Sections: {len(doc.structure)}")
    
    print("\nFirst 10 Sections:")
    for i, section in enumerate(doc.structure[:10]):
        print(f"  {i+1}. [{section.level}] {section.title} (Length: {len(section.content)})")
        
except Exception as e:
    print(f"Error parsing PDF: {e}")
