import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI operations

import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

# Read data
df = pd.read_csv('Upload_Folder/extracted_data.csv')

def isSevere(symptom_str):
    severe = ['breathing problem', 'chest pain', 'breathlessness']
    sym_list = symptom_str.split(', ')
    return any(item.lower() in severe for item in sym_list)

def getGender(df, df2):
    df['PATIENT_GENDER'] = df['PATIENT_GENDER'].astype(str)
    df2['PATIENT_GENDER'] = df2['PATIENT_GENDER'].astype(str)
    df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
    
    M = [0, 0, 0]
    F = [0, 0, 0]

    for i in range(len(df2)):
        gen = df2.loc[i, 'PATIENT_GENDER']
        if gen == 'M':
            M[2] += 1
        elif gen == 'F':
            F[2] += 1

    for i in range(len(df)):
        gen = df.loc[i, 'PATIENT_GENDER']
        sym = df.loc[i, 'SYMPTOMS']
        severeflag = isSevere(sym)

        if gen == 'M':
            M[0] += 1
            M[1] += severeflag
        if gen == 'F':
            F[0] += 1
            F[1] += severeflag

    return {'M': M, 'F': F}

def getAge(df, df2):
    df['PATIENT_AGE'] = df['PATIENT_AGE'].astype(int)
    df2['PATIENT_AGE'] = df2['PATIENT_AGE'].astype(int)
    df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)

    age_ranges = {
        '18-30': [0, 0, 0],
        '31-40': [0, 0, 0],
        '41-50': [0, 0, 0],
        '51-60': [0, 0, 0],
        '61-70': [0, 0, 0],
        '71-80': [0, 0, 0],
        '81-90': [0, 0, 0],
        '91-100': [0, 0, 0]
    }

    for i in range(len(df2)):
        age = df2.loc[i, 'PATIENT_AGE']
        if 18 <= age <= 30:
            age_ranges['18-30'][2] += 1
        elif 31 <= age <= 40:
            age_ranges['31-40'][2] += 1
        elif 41 <= age <= 50:
            age_ranges['41-50'][2] += 1
        elif 51 <= age <= 60:
            age_ranges['51-60'][2] += 1
        elif 61 <= age <= 70:
            age_ranges['61-70'][2] += 1
        elif 71 <= age <= 80:
            age_ranges['71-80'][2] += 1
        elif 81 <= age <= 90:
            age_ranges['81-90'][2] += 1
        elif 91 <= age <= 100:
            age_ranges['91-100'][2] += 1

    for i in range(len(df)):
        age = df.loc[i, 'PATIENT_AGE']
        sym = df.loc[i, 'SYMPTOMS']
        severeflag = isSevere(sym)
        
        if 18 <= age <= 30:
            age_ranges['18-30'][0] += 1
            age_ranges['18-30'][1] += severeflag
        elif 31 <= age <= 40:
            age_ranges['31-40'][0] += 1
            age_ranges['31-40'][1] += severeflag
        elif 41 <= age <= 50:
            age_ranges['41-50'][0] += 1
            age_ranges['41-50'][1] += severeflag
        elif 51 <= age <= 60:
            age_ranges['51-60'][0] += 1
            age_ranges['51-60'][1] += severeflag
        elif 61 <= age <= 70:
            age_ranges['61-70'][0] += 1
            age_ranges['61-70'][1] += severeflag
        elif 71 <= age <= 80:
            age_ranges['71-80'][0] += 1
            age_ranges['71-80'][1] += severeflag
        elif 81 <= age <= 90:
            age_ranges['81-90'][0] += 1
            age_ranges['81-90'][1] += severeflag
        elif 91 <= age <= 100:
            age_ranges['91-100'][0] += 1
            age_ranges['91-100'][1] += severeflag

    return age_ranges

def getSymptoms(df):
    symp = df.SYMPTOMS.str.split(', ', expand=True).stack().value_counts()
    symp_dict = symp.head(10).to_dict()
    symp_dict.pop("adverse effect of covid vaccine", None)
    symp_dict.pop("nan", None)
    return symp_dict

def plot_gender_distribution(df, df2):
    data = getGender(df, df2)
    labels = ['Male', 'Female']
    counts = [data['M'][0], data['F'][0]]
    severe_counts = [data['M'][1], data['F'][1]]
    
    fig, ax = plt.subplots()
    bar_width = 0.35
    index = range(len(labels))
    
    bar1 = ax.bar(index, counts, bar_width, label='Total Cases')
    bar2 = ax.bar([i + bar_width for i in index], severe_counts, bar_width, label='Severe Cases')
    
    ax.set_xlabel('Gender')
    ax.set_ylabel('Count')
    ax.set_title('Adverse Effects by Gender')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(labels)
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return img_str

def plot_age_distribution(df, df2):
    data = getAge(df, df2)
    age_ranges = list(data.keys())
    total_counts = [data[age_range][0] for age_range in age_ranges]
    severe_counts = [data[age_range][1] for age_range in age_ranges]
    
    fig, ax = plt.subplots()
    bar_width = 0.35
    index = range(len(age_ranges))
    
    bar1 = ax.bar(index, total_counts, bar_width, label='Total Cases')
    bar2 = ax.bar([i + bar_width for i in index], severe_counts, bar_width, label='Severe Cases')
    
    ax.set_xlabel('Age Range')
    ax.set_ylabel('Count')
    ax.set_title('Adverse Effects by Age Range')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(age_ranges, rotation=45, ha='right')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return img_str

def plot_symptom_distribution(df):
    symp_dict = getSymptoms(df)
    symptoms = list(symp_dict.keys())
    counts = list(symp_dict.values())
    
    fig, ax = plt.subplots()
    ax.barh(symptoms, counts)
    
    ax.set_xlabel('Count')
    ax.set_ylabel('Symptoms')
    ax.set_title('Top 10 Symptoms')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return img_str
