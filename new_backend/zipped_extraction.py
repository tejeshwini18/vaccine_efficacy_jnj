import os
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
import cv2
import zipfile
from PIL import Image

# Tesseract installation path (ensure this path is correct for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to convert image to black and white
def convert_to_bw(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return bw

# Function to extract text and important values from a PDF
def extract_data_from_pdf(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    page = doc.load_page(0)  # Load the first page
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    
    # Save the page as an image
    img_path = 'output.png'
    pix.save(img_path)

    # Read the image using OpenCV
    img = cv2.imread(img_path)
    text = pytesseract.image_to_string(img)

    # Example of extracting specific fields using image cropping
    bp_image = img[520:560, 5:310]      # Crop the image to get the BP value
    height_image = img[520:560, 330:570]
    weight_image = img[520:560, 550:780]
    pulse_image = img[520:560, 800:980]
    spo2_image = img[520:560, 980:1150]

    # Convert to black and white for better OCR accuracy on certain sections
    bp_image_bw = convert_to_bw(bp_image)
    spo2_image_bw = convert_to_bw(spo2_image)

    # Extract text from cropped images
    bp = pytesseract.image_to_string(bp_image)
    height = pytesseract.image_to_string(height_image)
    weight = pytesseract.image_to_string(weight_image)
    pulse = pytesseract.image_to_string(pulse_image)
    spo2 = pytesseract.image_to_string(spo2_image_bw)

    return text, bp, height, weight, pulse, spo2

# Function to extract structured data from OCR text
def extract_structured_data(text, bp, height, weight, pulse, spo2):
    def between(value, a, b):
        pos_a = value.find(a)
        if pos_a == -1: return ""
        pos_b = value.rfind(b)
        if pos_b == -1: return ""
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b: return ""
        return value[adjusted_pos_a:pos_b].strip()

    # Extract relevant fields
    data = {
        'Clinic Name': 'Princeton Hospital',
        'Clinic Address': between(text, "Address:", "Phone"),
        'Clinic Contact': between(text, "Phone:", "Email"),
        'Doctor Name': between(text, "Doctor's Name-", "Next"),
        'Date of Visit': between(text, "Date of visit-", "SSN"),
        'Patient Name': between(text, "Patient Name-", "Address"),
        'Patient Age': between(text, "Age-", "Gender"),
        'Symptoms': between(text, "Problems:", "Vaccination Name"),
        'Blood Pressure': bp,
        'Height': height,
        'Weight': weight,
        'Pulse Rate': pulse,
        'SPO2': spo2,
        'Diagnosis': between(text, "Diagnosis-", "Medicines"),
        'Medicines': between(text, "Duration", "Suggested"),
        'Follow Up Date': between(text, "Next Visit Date-", ""),
    }

    return data

# Function to process the extracted files and store data in a CSV
def process_uploaded_files(zip_file_path):
    extraction_folder = './Upload_Folder/'
    
    # Extract files from the uploaded zip
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extraction_folder)

    # List all the files in the dataset folder
    files = os.listdir(extraction_folder)

    # Initialize DataFrame to store extracted data
    df = pd.DataFrame(columns=[
        'Clinic Name', 'Clinic Address', 'Clinic Contact', 'Doctor Name', 'Date of Visit', 
        'Patient Name', 'Patient Age', 'Symptoms', 'Blood Pressure', 'Height', 'Weight', 
        'Pulse Rate', 'SPO2', 'Diagnosis', 'Medicines', 'Follow Up Date'
    ])

    # List to collect extracted data
    extracted_data_list = []

    # Iterate through each file and extract data
    for i, file in enumerate(files):
        file_path = os.path.join(extraction_folder, file)
        if file.endswith('.pdf'):  # Process only PDF files
            try:
                text, bp, height, weight, pulse, spo2 = extract_data_from_pdf(file_path)
                extracted_data = extract_structured_data(text, bp, height, weight, pulse, spo2)
                
                # Append extracted data to the list
                extracted_data_list.append(extracted_data)
                print(f"Extracted data from {file}")

            except Exception as e:
                print(f"Error extracting data from {file}: {e}")

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(extracted_data_list)

    # Save extracted data to CSV
    output_csv = './Upload_Folder/extracted_data.csv'
    df.to_csv(output_csv, index=False)
    print(f"Data extraction complete. CSV saved at {output_csv}")
    return output_csv
