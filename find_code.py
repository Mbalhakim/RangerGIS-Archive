import easyocr
from pdf2image import convert_from_path
import numpy as np
import re

# Convert PDF to images
def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)

# Apply EasyOCR to detect all handwritten text
def extract_handwritten_text(image):
    # Convert PIL image to numpy array for EasyOCR
    image_np = np.array(image)
    
    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])
    
    # Detect text in the image
    result = reader.readtext(image_np)
    
    # Extract and return all detected text
    extracted_text = "\n".join([text[1] for text in result])
    return extracted_text

# Extract text that follows the keyword
def extract_text_after_keyword(text, keyword):
    # Use regex to find the text that comes after the keyword
    pattern = rf'{keyword}\s*(.*)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

# Main processing function for PDFs
def process_pdf_for_handwritten_text(pdf_path, keyword):
    images = convert_pdf_to_images(pdf_path)
    found_text = None  # To store the first occurrence

    for page_num, image in enumerate(images):
        print(f"Processing page {page_num + 1}...")

        # Extract all handwritten text with EasyOCR
        handwritten_text = extract_handwritten_text(image)

        # Extract text after the specified keyword
        text_after_keyword = extract_text_after_keyword(handwritten_text, keyword)

        if text_after_keyword:
            found_text = text_after_keyword
            print(f"Place code found on page: {page_num + 1}: {found_text}")
            break
        else:
            print(f"No text found after the word '{keyword}' on page {page_num + 1}.\n")

    if found_text is None:
        print(f"No occurrence of '{keyword}' found in the document.")

# Example usage
pdf_path = 'C:/Users/Hussain/OneDrive - Hanzehogeschool Groningen/GIS Archive Project/OneDrive_2024-10-21/Testdocumenten ter hernoeming/Documenten met enkel plaatscode/ZX.pdf'  # Replace with the path to your PDF
keyword = 'Dossier'
process_pdf_for_handwritten_text(pdf_path, keyword)
