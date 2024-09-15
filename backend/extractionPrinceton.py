import pandas as pd
from IPython.display import display,HTML
import fitz
import pytesseract
import cv2
import os
pytesseract.pytesseract.tesseract_cmd=r'C:\Users\1945686\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
from PIL import Image
from codecarbon import track_emissions
from codecarbon import EmissionsTracker
import re

def convert2BW(img):   
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    (thresh, bw) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return bw

def pdf2text(file):
    # for converting pdf to image 
    mat=fitz.Matrix(2.0,2.0)
    doc=fitz.open(file)
    page=doc.load_page(0)
    pix=page.get_pixmap(matrix=mat)
    pix.save('output.png')
    # extract text from image
    img=cv2.imread('output.png')
    text=pytesseract.image_to_string(img)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    (thresh, bw) = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    cv2.imwrite('output1.png',bw)
    im=Image.open('output.png')
    im3=Image.open('output1.png')
    # width, height=im.size
    # print(width,height)
    # im1=im.crop((5,500,1150,600))
    # text2=pytesseract.image_to_string(im1)

    BP=im.crop((5,520,310,560))
    height=im.crop((330,520,570,560))
    weight=im.crop((550,520,780,560))
    pulse=im.crop((800,520,980,560))
    spo2=im3.crop((980,520,1150,560))
    # BP=convert2BW(BP)
    # height=convert2BW(height)
    # weight=convert2BW(weight)
    # pulse=convert2BW(pulse)
    # spo2=convert2BW(spo2)
    BP=pytesseract.image_to_string(BP)
    height=pytesseract.image_to_string(height)
    weight=pytesseract.image_to_string(weight)
    pulse=pytesseract.image_to_string(pulse)
    spo2=pytesseract.image_to_string(spo2)
    return text,BP,height,weight,pulse,spo2

# reading path
path="./UploadFolder/dataset"
paths=os.listdir(path) 

# DataFrame for storing Data
df=pd.DataFrame({
    'CLINIC_NAME':[],
    'CLINIC_ADDRESS':[],
    'CLINIC_CONTACT':[],
    'CLINIC_EMAIL':[],
    'DOCTOR_NAME':[],
    'DOCTOR_SSN':[],
    'DOCTOR_CONTACT':[],
    'DOCTOR_EMAIL':[],
    'DATE_OF_VISIT':[],
    'PATIENT_NAME':[],
    'PATIENT_DOB':[],
    'PATIENT_AGE':[],
    'PATIENT_ADDRESS':[],
    'PATIENT_CONTACT':[],
    'PATIENT_EMAIL':[],
    'PATIENT_SSN':[],
    'PATIENT_HID':[],
    'PATIENT_GENDER':[],
    'SYMPTOMS':[],
    'OBSERVATION':[],
    'BLOOD_PRESSURE':[],
    'PULSE_RATE':[],
    'SPO2':[],
    'HEIGHT':[],
    'WEIGHT':[],
    'COVID_VACCINE_STATUS':[],
    'COVID_VACCINE_NAME':[],
    'DOSE1_ON':[],
    'DOSE2_ON':[],
    'BOOSTER_ON':[],
    'DIAGNOSIS':[],
    'MEDICINES':[],

    'LAB_INVESTIGATION':[],
    'ADVICE':[],

    'FOLLOW_UP_DATE':[]
})

# For Fetching Data between words
def between(value, a,b):
    pos_a=value.find(a)
    if pos_a== -1:
        return ""
    pos_b= value.rfind(b)
    if pos_b == -1:
        return ""
    adjusted_pos_a= pos_a + len(a)
    if adjusted_pos_a>=pos_b:
        return ""
    text=value[adjusted_pos_a :pos_b]
    return text.strip()

# Extraction of Data
def extractData(text,BP,height,weight,pulse,spo2):
    CLINIC_NAME='Princeton Hospital'
    CLINIC_ADDRESS=between(text,"Address:","Phone")
    CLINIC_CONTACT=between(text,"Phone:","Email")
    CLINIC_EMAIL=between(text,"Email:","Date of")
    DOCTOR_NAME=between(text,"Doctor's Name-","Next")
    DOCTOR_SSN=' '
    DOCTOR_CONTACT=' '
    DOCTOR_EMAIL=' '
    DATE_OF_VISIT=between(text,"Date of visit-","SSN")
    PATIENT_NAME=between(text,"Patient Name-","Address")
    PATIENT_DOB=' '
    PATIENT_AGE=between(text,"Age-","Gender")
    PATIENT_ADDRESS=between(text,"Address-","Age")
    PATIENT_CONTACT=' '
    PATIENT_EMAIL=' '
    PATIENT_SSN=between(text,"SSN-","Health ID")
    PATIENT_HID=between(text,"Health ID-","Patient")
    gender=between(text,"Gender-","\n")
    PATIENT_GENDER=gender.split(' ', 1)[0]
    SYMPTOMS=between(text,"Problems:","Vaccination Name")
    OBSERVATION=between(text,"Observation-","Diagnosis")
    BLOOD_PRESSURE=between(BP,"Blood Pressure","")
    PULSE_RATE=between(pulse,"Pulse","")
    SPO2=between(spo2,"SPO2","")
    HEIGHT=between(height,"Height","")
    WEIGHT=between(weight,"Weight","")
    vaccination=between(text,"Vaccination Status:","Observation")
    vac=vaccination.split(' ')
    vac2=' '.join(vac[1:3])
    COVID_VACCINE_STATUS=vac2
    COVID_VACCINE_NAME=vac[0]
    DOSE1_ON=' '
    DOSE2_ON=' '
    BOOSTER_ON=' '
    DIAGNOSIS=between(text,"Diagnosis-","Medicines")
    MEDICINES=between(text,"Duration","Suggested")
    LAB_INVESTIGATION=between(text,"Investigation-","Advice")
    ADVICE=between(text,"Advice-","Doctor")
    FOLLOW_UP_DATE=between(text,"Next Visit Date-","")
    df.loc[len(df.index)]= [CLINIC_NAME,CLINIC_ADDRESS,CLINIC_CONTACT,CLINIC_EMAIL,DOCTOR_NAME,DOCTOR_SSN,DOCTOR_CONTACT,DOCTOR_EMAIL,DATE_OF_VISIT,PATIENT_NAME,PATIENT_DOB,PATIENT_AGE,PATIENT_ADDRESS,PATIENT_CONTACT,PATIENT_EMAIL,PATIENT_SSN,PATIENT_HID,PATIENT_GENDER,SYMPTOMS,OBSERVATION,BLOOD_PRESSURE,PULSE_RATE,SPO2,HEIGHT,WEIGHT,COVID_VACCINE_STATUS,COVID_VACCINE_NAME,DOSE1_ON,DOSE2_ON,BOOSTER_ON,DIAGNOSIS,MEDICINES,LAB_INVESTIGATION,ADVICE, FOLLOW_UP_DATE]

def extract():
    i=1
    print("Data Extraction Started..")
    for item in paths:
        filepath=path+'/'+item
        text,BP,height,weight,pulse,spo2=pdf2text(filepath)
        extractData(text,BP,height,weight,pulse,spo2)
        # display(df)
        print("Extracting Data from Prescription: "+ str(i))
        i+=1
        if(i>5):
            break
    df.to_csv('data.csv')
# print(text2)
# extractData(text)
# display(df)
