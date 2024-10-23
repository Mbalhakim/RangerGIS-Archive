import cv2
import numpy as np
import pytesseract
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from PIL import Image
from pdf2image import convert_from_path

# Set up pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # Adjust if needed

# Convert PDF to images
def pdf_to_images(pdf_path, dpi=300):
    images = convert_from_path(pdf_path, dpi)
    return images

# Preprocess image (resize, grayscale, thresholding)
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    # Thresholding
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return binary

# Simple CNN-based text recognizer model
def build_cnn_model(input_shape):
    model = Sequential()

    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    
    model.add(Dense(1, activation='sigmoid'))  # This is a binary classifier, adapt for OCR if needed
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

# Train CNN model (dummy function, needs proper dataset)
def train_model():
    # Placeholder for training data, typically you would use labeled images and characters
    # X_train, y_train would be your dataset
    model = build_cnn_model((64, 64, 1))
    
    # Placeholder for fitting, as training requires proper data
    # model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_val, y_val))
    
    return model

# Perform OCR using Tesseract
def perform_ocr(image):
    text = pytesseract.image_to_string(image)
    return text

# Recognize text from an image or PDF
def recognize_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        images = pdf_to_images(file_path)
    else:
        images = [Image.open(file_path)]

    texts = []
    for image in images:
        processed_image = preprocess_image(image)
        text = perform_ocr(processed_image)
        texts.append(text)
    
    return "\n".join(texts)

# Example usage
if __name__ == "__main__":
    file_path = 'your_image_or_pdf.pdf'  # Input image or PDF path
    extracted_text = recognize_text_from_file(file_path)
    print("Extracted Text: \n", extracted_text)
