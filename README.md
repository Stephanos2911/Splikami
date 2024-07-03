# Curaçao Newspaper Preservation

This Python application is designed to assist in the preservation and digitization of newspapers from the island of Curaçao. The application extracts text from scanned newspaper images, converts them into searchable PDF format, categorizes the content, and stores metadata in a SQLite database for easy access and retrieval.

## Features

- **OCR Processing**: Uses Tesseract OCR to extract text from scanned newspaper images.
- **Image Processing**: Utilizes the Pillow library to handle image conversions and preprocessing.
- **PDF Conversion**: Converts images to PDF format using PyMuPDF and integrates OCR text for searchability.
- **Category Determination**: Categorizes the content based on predefined keywords in Dutch.
- **Database Storage**: Stores metadata and processed data in a SQLite database for easy access.

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create a Virtual Environment**
    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment**
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4. **Install the Required Packages**
    ```bash
    pip install -r requirements.txt
    ```

### Tesseract OCR Installation

#### Windows

1. Download the Tesseract installer from [UB Mannheim Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer and follow the installation instructions. Don't forget to install the language pack to support Dutch.
3. [Add the Tesseract OCR executable to your system's PATH](https://youtu.be/Rb93uLXiTwA?si=vTJ-jZinbfabBk0K&t=249) in the System Environment Variables menu. Typically, the path is `C:\Program Files\Tesseract-OCR\tesseract.exe` (refer to the .Exe and NOT the folder). 

#### macOS

1. Use Homebrew to install Tesseract. If you don't have Homebrew installed, you can install it from [Homebrew](https://brew.sh/).
    ```bash
    brew install tesseract
    ```

#### Linux (Ubuntu/Debian)

1. Install Tesseract using apt-get.
    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr
    ```

## Usage

1. **Activate the Virtual Environment**
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

2. **Run the Application**
    ```bash
    python src/main.py
    ```

3. **Add Newspaper Scans**
    - Place your scanned newspaper images (pdf) in the `Docs` directory.
    - The application will automatically process these PDFs, extract the text, categorize the content, and store the metadata in the SQLite database.
