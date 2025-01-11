import re
import csv
import fitz  # PyMuPDF for reading PDFs

# Function to extract text from PDF within a specific page range
def extract_text_from_pdf(pdf_path, start_page, end_page):
    """
    Extract text from a PDF within a specific page range.
    :param pdf_path: Path to the PDF file.
    :param start_page: Start page number (1-based).
    :param end_page: End page number (1-based).
    :return: Extracted text as a string.
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in range(start_page - 1, end_page):  # 0-based indexing in PyMuPDF
            text += doc[page_num].get_text()
    return text

# Function to extract sections from the text
def extract_sections(text):
    # Match patterns for PURPORT and TEXT followed by numbers
    sections = re.split(r'(TEXTS? \d+(?:-\d+)?)', text)
    
    data = []
    current_section = ""

    # Iterate through the split sections and categorize
    for i in range(len(sections)):
        if sections[i].startswith("TEXT") or sections[i] == "PURPORT":
            if current_section:
                data.append(current_section.strip())
            current_section = f'{sections[i]}:'  # Start new section
        else:
            current_section += f' {sections[i]}'  # Append text to current section

    # Append the last section if any
    if current_section:
        data.append(current_section.strip())
    
    return data

# Function to save data into CSV
def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Index', 'Text'])
        for idx, text in enumerate(data):
            writer.writerow([idx + 1, text])

# Input PDF file path and page range
pdf_path = 'gitaEdition.pdf'
start_page = 64  # Change to your desired start page
end_page = 107   # Change to your desired end page

# Extract text from the given page range in the PDF file
input_text = extract_text_from_pdf(pdf_path, start_page, end_page)

# Extract and save
sections = extract_sections(input_text)
save_to_csv(sections, 'gita_sections.csv')

print("CSV file 'gita_sections.csv' created successfully!")
