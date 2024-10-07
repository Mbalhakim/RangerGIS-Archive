import exifread
import fitz  # PyMuPDF
import numpy as np
import pytesseract
import cv2
import io
from PIL import Image

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Function to detect if an image is likely a satellite image based on its color profile
def is_satellite_image(image_np):
    # Convert image to HSV (Hue, Saturation, Value) color space
    hsv_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)

    # Define range for detecting green areas (which are common in satellite images)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    # Mask for green areas
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    # Count the number of green pixels
    green_pixel_count = np.sum(green_mask > 0)

    # Define range for detecting brown (common for land areas in satellite images)
    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([20, 255, 200])

    # Mask for brown areas
    brown_mask = cv2.inRange(hsv_image, lower_brown, upper_brown)

    # Count the number of brown pixels
    brown_pixel_count = np.sum(brown_mask > 0)

    # Define a threshold; if green and brown pixels dominate the image, we assume it's satellite
    total_pixels = image_np.shape[0] * image_np.shape[1]
    if green_pixel_count + brown_pixel_count > 0.3 * total_pixels:
        return True
    return False


# Function to extract text and images from PDF
def extract_pdf_content(pdf_path):
    doc = fitz.open(pdf_path)
    content = {}

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # Extract text
        text = page.get_text("text")
        content[page_num] = {"text": text, "images": []}

        # Extract images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image = Image.open(io.BytesIO(image_bytes))
            image_path = f"page_{page_num}_image_{img_index}.{image_ext}"
            image.save(image_path)

            # Convert the image to OpenCV format for processing
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Check if the image is likely a satellite image
            if is_satellite_image(image_np):
                image_type = "Satellite Image"
            else:
                image_type = "Other Image"

            # Apply OCR on the image (for handwritten text or text extraction)
            image_text = pytesseract.image_to_string(image_np, config='--psm 6')

            content[page_num]["images"].append({
                "image_path": image_path,
                "image_type": image_type,  # Store the image type (satellite or other)
                "image_text": image_text
            })

    return content


def extract_gps_info(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)

    # Extract GPS metadata
    gps_latitude = tags.get('GPS GPSLatitude')
    gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
    gps_longitude = tags.get('GPS GPSLongitude')
    gps_longitude_ref = tags.get('GPS GPSLongitudeRef')

    if gps_latitude and gps_longitude:
        # Convert latitude and longitude to decimal
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = -lon

        return lat, lon
    else:
        return None, None

# Function to convert GPS coordinates to degrees
def convert_to_degrees(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

# Example usage
image_path = r'C:\Users\Mbhst\Desktop\Satleit-images.png'
latitude, longitude = extract_gps_info(image_path)

if latitude and longitude:
    print(f"Image was taken at Latitude: {latitude}, Longitude: {longitude}")
else:
    print("No GPS data found in the image.")
# Example usage
pdf_path = r'C:\Users\Mbhst\Desktop\TestDoc2.pdf'
extracted_content = extract_pdf_content(pdf_path)

# Output extracted data
for page, data in extracted_content.items():
    print(f"\nPage {page}:")
    print("Text:", data["text"])
    for img_data in data["images"]:
        print(f"Image Path: {img_data['image_path']}")
        print(f"Image Type: {img_data['image_type']}")
        print(f"Image Text: {img_data['image_text']}")
