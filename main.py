import pytesseract
from PIL import Image
import sqlite3
import fitz 
import os

# Function to convert a single-page PDF to an image using PyMuPDF and then perform OCR
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Load the first page
        pix = page.get_pixmap()  # Render the page to an image
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

# Predefined category keywords in Dutch
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

# Function to determine the category based on the most matching keywords
def determine_category_and_keywords(text):
    category_count = {category: 0 for category in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                category_count[category] += 1

    # Find the category with the most matches
    max_category = max(category_count, key=category_count.get)

    if category_count[max_category] > 0:
        return max_category, CATEGORY_KEYWORDS[max_category]
    else:
        return "", []

# Save text and file path to SQLite database
def save_to_db(file_path, text, category, keywords, db_name='documents.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents
                      (id INTEGER PRIMARY KEY, file_path TEXT UNIQUE NOT NULL, content TEXT, category TEXT, keywords TEXT)''')
    try:
        keywords_str = ', '.join(keywords)
        cursor.execute('INSERT OR IGNORE INTO documents (file_path, content, category, keywords) VALUES (?, ?, ?, ?)', (file_path, text, category, keywords_str))
    except sqlite3.IntegrityError:
        print("Duplicate entry found, skipping insert.")
    conn.commit()
    conn.close()

# Process individual document
def process_document(file_path):
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    category, keywords = determine_category_and_keywords(text)
    save_to_db(file_path, text, category, keywords)

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

            cursor.execute('SELECT * FROM documents WHERE category = ?', (selected_category,))
            records = cursor.fetchall()

            clear_console()
            if records:
                for record in records:
                    print(f"ID: {record[0]}")
                    print(f"File Path: {record[1]}")
                    print(f"Content: {record[2]}")
                    print(f"Category: {record[3]}")
                    print(f"Keywords: {record[4]}\n")

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
