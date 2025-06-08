import os
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
import cv2
import zipfile
from PIL import Image
import shutil
import time
import re

# Set Tesseract path based on environment
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:  # Linux (Heroku)
    pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'

# Create Upload_Folder if it doesn't exist
UPLOAD_FOLDER = './Upload_Folder'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Output folder for cropped images debug
DEBUG_IMAGE_DIR = os.path.join(UPLOAD_FOLDER, 'debug_images')
os.makedirs(DEBUG_IMAGE_DIR, exist_ok=True)

def search(column):
    # List of common vaccine-related symptoms
    vaccine_symptoms = [
        'fever', 'headache', 'fatigue', 'muscle pain', 'chills', 'nausea',
        'vomiting', 'diarrhea', 'stomach pain', 'sore throat', 'cough',
        'shortness of breath', 'chest pain', 'dizziness', 'rash', 'swelling',
        'joint pain', 'body ache', 'loss of appetite', 'sleepiness'
    ]
    
    try:
        text = str(column).lower()
        print(f"\nSearching in text: {text}")
        
        # Check if any vaccine-related symptoms are present
        symptoms_found = [symptom for symptom in vaccine_symptoms if symptom in text]
        if symptoms_found:
            print(f"Found vaccine-related symptoms: {symptoms_found}")
            return True
            
        # Also check for explicit mentions of vaccine-related issues
        patterns = [
            r'.*(adverse|side|negative|complication|observed|-ve|effect).*(covid|vaccine|vaccination|vax)',
            r'.*(covid|vaccine|vaccination|vax).*(adverse|side|negative|complication|observed|-ve|effect)',
            r'.*(post.*vaccine|post.*vax|post.*covid).*(symptom|effect|reaction)',
            r'.*(symptom|effect|reaction).*(post.*vaccine|post.*vax|post.*covid)'
        ]
        
        for pattern in patterns:
            res = re.search(pattern, text)
            if res:
                print(f"Match found with pattern: {pattern}")
                return True
                
        print("No matches found")
        return False
    except Exception as e:
        print(f"Error in search function: {e}")
        return False

def convert_to_bw(img):
    """Convert image to black and white using adaptive thresholding."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return bw

def clean_extracted_text(text, field_type=''):
    """Clean extracted OCR text based on field type."""
    text = text.replace('|', '').replace('—', '').replace(' ', '').replace('\n', '')
    if field_type == 'bp':
        # Allow digits and forward slash
        text = ''.join(c for c in text if c.isdigit() or c == '/')
        # Add slash if missing but length looks like BP (e.g. 12078 -> 120/78)
        if '/' not in text and len(text) >= 5:
            text = text[:3] + '/' + text[3:]
    elif field_type in ['height', 'weight', 'pulse', 'spo2', 'age']:
        text = ''.join(c for c in text if c.isdigit())
    return text.strip()

def extract_field(image, coords, field_name, field_type=''):
    """
    Crop a region from image, preprocess it, save debug image, and extract text.
    coords: (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = coords
    cropped = image[y1:y2, x1:x2]

    bw_image = convert_to_bw(cropped)

    # Dilate to improve OCR
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    bw_image = cv2.dilate(bw_image, kernel, iterations=1)

    # Save cropped image for debugging
    debug_path = os.path.join(DEBUG_IMAGE_DIR, f"{field_name}.png")
    cv2.imwrite(debug_path, bw_image)

    # Tesseract config for single line recognition
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(bw_image, config=custom_config)

    cleaned_text = clean_extracted_text(text, field_type)
    return cleaned_text

def extract_data_from_pdf(file_path):
    """Extract required data fields from a single PDF file."""
    doc = None
    try:
        print(f"\nStarting PDF extraction for: {file_path}")
        doc = fitz.open(file_path)
        page = doc.load_page(0)  # First page
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        
        img_path = os.path.join(UPLOAD_FOLDER, 'output.png')
        pix.save(img_path)

        img = cv2.imread(img_path)
        if img is None:
            raise Exception(f"Failed to read image from {img_path}")

        # Define all regions to crop (x1, y1, x2, y2)
        regions = {
            'bp': (185, 520, 270, 560),
            'height': (480, 520, 595, 560),
            'weight': (710, 520, 780, 560),
            'pulse': (925, 520, 980, 560),
            'spo2': (1080, 520, 1170, 560),
            'gender': (680, 400, 900, 480),
            'age': (70, 400, 180, 450),
            'symptoms': (110, 600, 300, 650),
        }

        # Extract fields via OCR
        extracted = {}
        for field, coords in regions.items():
            # 'gender' is free text, others cleaned numerics except bp has slash
            field_type = 'gender' if field == 'gender' else field
            extracted[field] = extract_field(img, coords, field, field_type)

        # Extract full text for other structured fields
        full_text = pytesseract.image_to_string(img)
        print(f"\nExtracted full text from PDF:")
        print(full_text)

        # Helper to extract between two strings from full text
        def between(value, a, b):
            pos_a = value.find(a)
            if pos_a == -1: return ""
            pos_b = value.find(b, pos_a + len(a)) if b else len(value)
            if pos_b == -1: pos_b = len(value)
            adjusted_pos_a = pos_a + len(a)
            if adjusted_pos_a >= pos_b: return ""
            return value[adjusted_pos_a:pos_b].strip()

        # Extract other structured fields
        data = {
            'CLINIC_NAME': 'Princeton Hospital',
            'CLINIC_ADDRESS': between(full_text, "Address:", "Phone"),
            'CLINIC_CONTACT': between(full_text, "Phone:", "Email"),
            'DOCTOR_NAME': between(full_text, "Doctor's Name-", "Next"),
            'DATE_OF_VISIT': between(full_text, "Date of visit-", "SSN"),
            'PATIENT_NAME': between(full_text, "Patient Name-", "Address"),
            'PATIENT_AGE': extracted.get('age') or between(full_text, "Age-", "Gender"),
            'GENDER': extracted['gender'] or between(full_text, "Gender-", "Symptoms"),
            'SYMPTOMS': between(full_text, "Problems:", "Vaccination Name") or extracted.get('symptoms', ''),
            'BLOOD_PRESSURE': extracted['bp'],
            'HEIGHT': extracted['height'],
            'WEIGHT': extracted['weight'],
            'PULSE_RATE': extracted['pulse'],
            'SPO2': extracted['spo2'],
            'DIAGNOSIS': between(full_text, "Diagnosis-", "Medicines"),
            'MEDICINES': between(full_text, "Duration", "Suggested"),
            'FOLLOW_UP_DATE': between(full_text, "Next Visit Date-", ""),
        }

        # Print extracted symptoms for debugging
        print(f"\nExtracted symptoms: {data['SYMPTOMS']}")

        # Standardize gender
        g = data['GENDER'].strip().upper()
        if 'MALE' in g or g == 'M':
            data['GENDER'] = 'M'
        elif 'FEMALE' in g or g == 'F':
            data['GENDER'] = 'F'
        else:
            data['GENDER'] = ''

        print(f"Extracted Data from {os.path.basename(file_path)}:\n{data}")

        return full_text, data['BLOOD_PRESSURE'], data['HEIGHT'], data['WEIGHT'], \
               data['PULSE_RATE'], data['SPO2'], data['GENDER'], data['PATIENT_AGE'], data['SYMPTOMS']

    except Exception as e:
        print(f"Error in extract_data_from_pdf: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise
    finally:
        if doc:
            doc.close()

def process_uploaded_files(zip_file_path):
    """Extract data from all PDFs inside a ZIP file and save to CSV."""
    temp_dir = None
    try:
        if not os.path.exists(zip_file_path):
            raise FileNotFoundError(f"ZIP file not found: {zip_file_path}")

        print(f"Processing zip file: {zip_file_path}")

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print("\nContents of ZIP file:")
            for file_info in zip_ref.infolist():
                print(f"- {file_info.filename}")

            temp_dir = os.path.join(UPLOAD_FOLDER, 'temp_extract')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            zip_ref.extractall(temp_dir)
            print(f"Extracted files to: {temp_dir}")

        def find_pdf_files(directory):
            pdfs = []
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdfs.append(os.path.join(root, file))
            return pdfs

        pdf_files = find_pdf_files(temp_dir)
        print(f"Found {len(pdf_files)} PDF files.")

        if not pdf_files:
            raise Exception("No PDF files found in the uploaded ZIP")
            
        results = []
        for pdf_file in pdf_files:
            try:
                extracted = extract_data_from_pdf(pdf_file)
                results.append(extracted)
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        # Save results to CSV
        df = pd.DataFrame(results, columns=[
            "FULL_TEXT", "BLOOD_PRESSURE", "HEIGHT", "WEIGHT",
            "PULSE_RATE", "SPO2", "GENDER", "PATIENT_AGE", "SYMPTOMS"
        ])

        # Print sample of symptoms for debugging
        print("\nSample of symptoms found:")
        print(df['SYMPTOMS'].head())
        
        # Save the complete extracted data
        extracted_csv_path = os.path.join(UPLOAD_FOLDER, "extracted_data.csv")
        df.to_csv(extracted_csv_path, index=False)
        print(f"Complete data saved to: {extracted_csv_path}")
        
        # Create and save adverse effects data
        print("\nFiltering for adverse effects...")
        df_adverse = df[df['SYMPTOMS'].apply(lambda x: search(str(x)))]
        print(f"Found {len(df_adverse)} records with adverse effects")
        
        if len(df_adverse) > 0:
            print("\nSample of adverse effects found:")
            print(df_adverse['SYMPTOMS'].head())
        
        adverse_path = os.path.join(UPLOAD_FOLDER, 'AdverseEffect.csv')
        df_adverse.to_csv(adverse_path, index=False)
        print(f"Adverse effects data saved to: {adverse_path}")
        
        # Create and save filtered data (copy of extracted data for now)
        filtered_path = os.path.join(UPLOAD_FOLDER, 'Filtered_Data.csv')
        df.to_csv(filtered_path, index=False)
        print(f"Filtered data saved to: {filtered_path}")

        return extracted_csv_path

    except Exception as e:
        print(f"Error in process_uploaded_files: {e}")
        raise
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
