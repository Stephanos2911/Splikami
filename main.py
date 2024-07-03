import pytesseract
from PIL import Image
import sqlite3
from pdf2image import convert_from_path
import os

# Function to convert PDF to images
def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)

# Function to perform OCR on an image
def ocr_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

# Expanded predefined category keywords in Dutch
CATEGORY_KEYWORDS = {
    "financieel": ["factuur", "ontvangst", "betaling", "saldo", "rekening", "kosten", "uitgave", "inkomsten", "boeking", "bankafschrift"],
    "juridisch": ["contract", "overeenkomst", "wet", "naleving", "advocaat", "rechtszaak", "jurisprudentie", "getuigenis", "vonnis", "clausule"],
    "medisch": ["patiënt", "diagnose", "behandeling", "voorschrift", "medicatie", "symptomen", "therapie", "onderzoek", "ziekenhuis", "consultatie"],
    "onderwijs": ["huiswerk", "college", "examen", "opdracht", "scriptie", "studie", "school", "docent", "les", "vak", "tentamen"],
    "politiek": ["verkiezingen", "regering", "parlement", "democratie", "politicus", "beleid", "partij", "kiesdistrict", "stemmen", "minister"],
    "economie": ["groei", "werkloosheid", "inflatie", "markt", "handel", "industrie", "consument", "bestedingen", "inkomen", "investeringen"],
    "technologie": ["innovatie", "software", "hardware", "internet", "gadget", "app", "programma", "data", "netwerk", "robotica"],
    "sport": ["voetbal", "wedstrijd", "kampioenschap", "coach", "atleet", "record", "competitie", "score", "team", "training"],
    "cultuur": ["kunst", "museum", "theater", "film", "muziek", "literatuur", "tentoonstelling", "festival", "concert", "dans"],
    "milieu": ["klimaat", "vervuiling", "recycling", "natuur", "duurzaamheid", "energie", "ecosysteem", "broeikaseffect", "afval", "biodiversiteit"],
    "wetenschap": ["onderzoek", "experiment", "theorie", "wetenschapper", "universiteit", "studie", "laboratorium", "publicatie", "ontdekking", "technologie"],
    "gezondheid": ["gezondheid", "ziekte", "preventie", "voeding", "sport", "mentaal", "fitheid", "medicatie", "ziekenhuis", "dokter"],
    "reizen": ["vakantie", "toerisme", "hotel", "vlucht", "bestemming", "bezienswaardigheid", "excursie", "avontuur", "paspoort", "visum"],
    "geschiedenis": ["tijdperk", "oorlog", "koning", "revolutie", "ontdekking", "keizerrijk", "dynastie", "monarchie", "historicus", "archeologie"],
    "entertainment": ["film", "serie", "acteur", "première", "bioscoop", "regisseur", "scene", "show", "comedy", "drama"]
}

# Function to determine categories based on keywords
def determine_categories(text):
    category_count = {category: 0 for category in CATEGORY_KEYWORDS}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                category_count[category] += 1
                
    # Find the category with the most matches
    max_category = max(category_count, key=category_count.get)
    
    if category_count[max_category] > 0:
        return max_category
    else:
        return ""

# Save text and file path to SQLite database
def save_to_db(file_path, text, categories, db_name='documents.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents
                      (id INTEGER PRIMARY KEY, file_path TEXT UNIQUE NOT NULL, content TEXT, categories TEXT)''')
    try:
        cursor.execute('INSERT OR IGNORE INTO documents (file_path, content, categories) VALUES (?, ?, ?)', (file_path, text, categories))
    except sqlite3.IntegrityError:
        print("Duplicate entry found, skipping insert.")
    conn.commit()
    conn.close()

# Process individual document
def process_document(file_path):
    if file_path.lower().endswith('.pdf'):
        images = pdf_to_images(file_path)
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            full_text += text
        categories = determine_categories(full_text)
        save_to_db(file_path, full_text, categories)
    else:
        text = ocr_image(file_path)
        categories = determine_categories(text)
        save_to_db(file_path, text, categories)

# Process all documents in the Docs folder
def process_all_documents(folder_path='Docs'):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            process_document(file_path)

# Function to display records by category
def display_records_by_category():
    conn = sqlite3.connect('documents.db')
    cursor = conn.cursor()
    
    while True:
        # Display all categories
        clear_console()
        print("\nSelect a category to view records:")
        for i, category in enumerate(CATEGORY_KEYWORDS.keys(), 1):
            print(f"{i}. {category}")
        print("0. Exit")
        
        choice = int(input("Enter the number of the category you want to see: "))
        
        if choice == 0:
            break
        
        if 1 <= choice <= len(CATEGORY_KEYWORDS):
            selected_category = list(CATEGORY_KEYWORDS.keys())[choice - 1]
            
            cursor.execute('SELECT * FROM documents WHERE categories LIKE ?', (f'%{selected_category}%',))
            records = cursor.fetchall()
            
            clear_console()
            if records:
                for record in records:
                    print(f"ID: {record[0]}")
                    print(f"Content: {record[1]}")
                    print(f"Categories: {record[2]}\n")
                    
                input("\n\nEnter any key to go back")
            else:
                print(f"No records found for the category: {selected_category}")
                input("\n\nEnter any key to go back")
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Example usage
process_all_documents()
display_records_by_category()