import os
import json
import re
from pypdf import PdfReader

PDF_FILE_PATH = "my_story.pdf"  # Put your 300-page PDF file name here

def extract_dynamic_chapters(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: Place your PDF file named '{pdf_path}' in the main folder.")
        return
        
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Successfully loaded PDF: {total_pages} pages found.")
    
    os.makedirs("chapters", exist_ok=True)
    
    chapters = []
    current_chapter_title = "Kapitel 1"
    current_chapter_text = []
    chapter_count = 1
    
    # Regex rule to look for common German chapter patterns: "Kapitel 1", "Kapitel I", "1. Die Reise"
    chapter_pattern = re.compile(r'^\s*(Kapitel\s+\d+|Kapitel\s+[IVXLCDM]+|\d+\.\s+[A-Z])', re.IGNORECASE)

    for page_num in range(total_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        if not text:
            continue
            
        lines = text.split('\n')
        
        for line in lines:
            # Check if this line marks the start of a completely new chapter section
            match = chapter_pattern.match(line)
            if match and len(current_chapter_text) > 2: # Ensure it doesn't instantly trigger on line 1
                # Save the completed chapter data structure first
                full_text = "\n".join(current_chapter_text)
                words = re.findall(r'[a-zA-ZäöüÄÖÜß]+', full_text)
                unique_words = list(set([w.lower() for w in words]))
                
                save_chapter(chapter_count, current_chapter_title, full_text, unique_words)
                
                # Reset buffers for the next variable length chapter
                chapter_count += 1
                current_chapter_title = line.strip()
                current_chapter_text = []
                
            current_chapter_text.append(line)
            
    # Don't forget to save the final chapter segment left at the end of the book
    if current_chapter_text:
        full_text = "\n".join(current_chapter_text)
        words = re.findall(r'[a-zA-ZäöüÄÖÜß]+', full_text)
        unique_words = list(set([w.lower() for w in words]))
        save_chapter(chapter_count, current_chapter_title, full_text, unique_words)

    # Output a central configuration catalog so the app frontend can map the index dropdown titles dynamically
    generate_catalog_index()

def save_chapter(index, title, text, unique_words):
    chapter_data = {
        "chapter_id": index,
        "title": title,
        "text": text,
        "vocabulary_count": len(unique_words)
    }
    with open(f"chapters/chapter_{index}.json", "w", encoding="utf-8") as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=4)
    print(f"Generated Chapter {index}: '{title}' containing {len(unique_words)} words.")

def generate_catalog_index():
    catalog = []
    chapter_files = sorted([f for f in os.listdir("chapters") if f.startswith("chapter_") and f.endswith(".json")], 
                           key=lambda x: int(re.search(r'\d+', x).group()))
    
    for file_name in chapter_files:
        with open(f"chapters/{file_name}", "r", encoding="utf-8") as f:
            data = json.load(f)
            catalog.append({
                "id": data["chapter_id"],
                "title": data["title"],
                "file": file_name
            })
            
    with open("chapters/catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)
    print("Catalog indexing finished successfully.")

if __name__ == "__main__":
    extract_dynamic_chapters(PDF_FILE_PATH)
