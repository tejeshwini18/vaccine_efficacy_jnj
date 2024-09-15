import pandas as pd
import numpy as np
import re



# DATA CLEANING
def filterdata():
    data=pd.read_csv('data.csv')
    data['PULSE_RATE'] = data['PULSE_RATE'].astype(str)
    for i in range(len(data)):
        pulse=data.loc[i,'PULSE_RATE']
        pulse=re.findall(r'\d{0,3}',pulse)[0]
        if(int(pulse=='')):
            pulse=0
        if(int(pulse)>=180 or int(pulse)<=60):
            pulse=None
        data.loc[i,'PULSE_RATE']=pulse


    data['SPO2'] = data['SPO2'].astype(str)
    for i in range(len(data)):
        spo2=data.loc[i,'SPO2']
        spo2=re.findall(r'\d{0,3}',spo2)[0]
        if(spo2==''):
            spo2=0
        if(float(spo2)>=100 or float(spo2)<=75):
            spo2=None
        data.loc[i,'SPO2']=spo2


    data['HEIGHT'] = data['HEIGHT'].astype(str)
    for i in range(len(data)):
        height=data.loc[i,'HEIGHT']
        height=re.findall(r'\d{0,3}',height)[0]
        if(height==''):
            height=0
        if(int(height)<50 or int(height)>250):
            height=None
        data.loc[i,'HEIGHT']=height
    data['PATIENT_GENDER']=data['PATIENT_GENDER'].str[:1]
    spec_chars=["!","#","%","&","'",",","*","+","-","|","{","}","[","]","<",">","?","$","~","`","!","^","(",")"]
    for char in spec_chars:
        data['BLOOD_PRESSURE']=data['BLOOD_PRESSURE'].str.replace(char,"")
    # mean_value=data['PULSE_RATE'].mean()
    # data['PULSE_RATE'].fillna(value=mean_value, inplace=True)
    # mean_value=data['HEIGHT'].mean()
    # data['HEIGHT'].fillna(value=mean_value, inplace=True)
    # mean_value=data['WEIGHT'].mean()
    # data['WEIGHT'].fillna(value=mean_value, inplace=True)
    # mean_value=data['SPO2'].mean()
    # data['SPO2'].fillna(value=mean_value, inplace=True)

    data['PATIENT_DOB']=data['PATIENT_DOB'].str.replace('00:00:00' ,'')
    data['DATE_OF_VISIT']=data['DATE_OF_VISIT'].str.replace('00:00:00' ,'')

    # FITERING DATA
    result=data.drop(['Unnamed: 0','CLINIC_CONTACT','CLINIC_NAME','CLINIC_ADDRESS','PATIENT_NAME','PATIENT_DOB','CLINIC_EMAIL','DOCTOR_NAME','DOCTOR_SSN','DOCTOR_CONTACT','DOCTOR_EMAIL','PATIENT_CONTACT'
    ,'PATIENT_EMAIL','PATIENT_SSN','PATIENT_HID','DOSE2_ON','BOOSTER_ON','MEDICINES','LAB_INVESTIGATION','ADVICE'],axis=1)
    coviddf=result[result['COVID_VACCINE_NAME']=='JANSSEN']
    coviddf.to_csv('CovidData.csv')
    return coviddf.to_dict()

def search(column):
    pattern=r'.*(adverse effect|side effect|negative effect|complication post|observed post|-ve effect).*covid.*(vaccine|vaccination)'
    res=re.search(pattern,column,re.IGNORECASE)
    if(res):
        return True
    else:
        return False

def adverseEffect():
    df=pd.read_csv('CovidData.csv')
    df=df.drop(['Unnamed: 0'],axis=1)
    df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
    df['OBSERVATION'] = df['OBSERVATION'].astype(str)

    df2=pd.DataFrame()
    for i in range(len(df)):
        observation=df.loc[i,'OBSERVATION']
        symptoms=df.loc[i,'SYMPTOMS']
        if(search(observation) or search(symptoms)):
            df2 = df2.append(df.iloc[i])
    
    df2.to_csv('AdverseEffect.csv')
    return df2.to_dict()

def efficacy():
    data=pd.read_csv('Updated_Main.csv')
    df=data.drop(['Unnamed: 0'],axis=1)
    covid_count=len(df[df['DIAGNOSIS'] == 'COVID +VE'])
    total_count=len(df)
    efficacy=(total_count-covid_count)/total_count*100
    return efficacy,covid_count
