import os
import json
import pytesseract
from pdf2image import convert_from_path
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from fuzzywuzzy import fuzz

# Set up Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_with_tesseract(image_path):
    # Open the image file
    image = cv2.imread(image_path)

    # Convert image to grayscale for better OCR accuracy
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(gray_image, lang='nld')  # Use 'nld' for Dutch
    return text

def convert_pdf_to_images(pdf_path):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    image_paths = []

    # Save each image as a temporary file
    for i, image in enumerate(images):
        image_path = f"temp_page_{i + 1}.png"
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

def load_json_data(json_file):
    # Load JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

def save_text_to_file(text, output_path):
    # Save the extracted text to a .txt file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def scan_pdf_and_match_codes(pdf_path, json_file, output_text_file):
    # Load the JSON file containing the list of codes
    data = load_json_data(json_file)

    # Create a dictionary of codes for quick lookup
    plaats_codes = {item["Naam object"]: item["PlaatsCode"] for item in data}

    print(f"Processing {pdf_path}...")

    # Convert PDF pages to images
    image_paths = convert_pdf_to_images(pdf_path)

    # Extract text from each image and combine
    combined_text = ""
    for image_path in image_paths:
        ocr_text = extract_text_with_tesseract(image_path)
        combined_text += ocr_text
        os.remove(image_path)  # Remove the temporary image file

    # Save the extracted text to a file
    save_text_to_file(combined_text, output_text_file)
    print(f"Extracted text saved to: {output_text_file}")

    # Calculate fuzzy matches
    match_results = []
    for naam_object, code in plaats_codes.items():
        match_percentage = fuzz.partial_ratio(code, combined_text)
        if match_percentage > 0:  # Consider only codes with some matching
            match_results.append((naam_object, code, match_percentage))

    # Sort by match percentage (descending) and select the top 10 matches
    match_results.sort(key=lambda x: x[2], reverse=True)
    top_matches = match_results[:10]

    # Output the result
    if top_matches:
        print(f"PDF: {os.path.basename(pdf_path)} - Top 10 Matched Codes:")
        for naam_object, code, match_percentage in top_matches:
            print(f"Naam object: {naam_object}, PlaatsCode: {code}, Match Percentage: {match_percentage}%")
    else:
        print(f"PDF: {os.path.basename(pdf_path)} - No matching codes found.")

    # Visualize only the matched codes and their percentages
    if top_matches:
        visualize_matched_codes(top_matches)

def visualize_matched_codes(top_matches):
    # Extract match data
    plaats_codes = [match[1] for match in top_matches]  # Only PlaatsCode as label
    percentages = [match[2] for match in top_matches]

    # Create a bar plot for match percentages
    plt.figure(figsize=(10, 6))
    sns.barplot(x=percentages, y=plaats_codes, hue=plaats_codes, palette="viridis", dodge=False, legend=False)
    plt.title('Top 10 Matched PlaatsCodes with Match Percentages')
    plt.xlabel('Match Percentage')
    plt.ylabel('PlaatsCode')
    plt.xlim(0, 100)  # Ensure the x-axis goes from 0 to 100%
    plt.show()



# Main execution
pdf_file = r"C:\Users\Mbhst\Desktop\Workspace\MachineLearning\Testdocumenten\DocumentenMetEnkelPlaatscode\ZY.pdf"  # Path to your PDF file
json_file = r"ObjectenLijst.json"  # Path to your JSON file
output_text_file = r"C:\Users\Mbhst\Desktop\Workspace\MachineLearning\RangerGIS-Archive\extracted_text.txt"  # Path to save the extracted text

scan_pdf_and_match_codes(pdf_file, json_file, output_text_file)
