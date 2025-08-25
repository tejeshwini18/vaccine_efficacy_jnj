import pandas as pd
import numpy as np
import re
import os

# DATA CLEANING
def filterdata():
    try:
        # Read the extracted data
        input_path = os.path.join('Upload_Folder', 'extracted_data.csv')
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        df = pd.read_csv(input_path)
        if df.empty:
            raise ValueError("No data found in extracted_data.csv")
            
        print(f"Total records in extracted_data.csv: {len(df)}")
        
        # Clean and format numeric columns
        numeric_columns = {
            'PULSE_RATE': (60, 100),
            'SPO2': (95, 100),
            'HEIGHT': (100, 250),
            'WEIGHT': (30, 150)
        }
        
        for col, (min_val, max_val) in numeric_columns.items():
            if col in df.columns:
                # Convert to numeric, coerce errors to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Replace values outside range with NaN
                df[col] = df[col].apply(lambda x: x if min_val <= x <= max_val else None)
        
        # Clean Blood Pressure
        if 'BLOOD_PRESSURE' in df.columns:
            df['BLOOD_PRESSURE'] = df['BLOOD_PRESSURE'].str.replace(r'[^\d/]', '', regex=True)
        
        # Clean Date of Visit
        if 'DATE_OF_VISIT' in df.columns:
            df['DATE_OF_VISIT'] = pd.to_datetime(df['DATE_OF_VISIT'], errors='coerce').dt.date
        
        # Clean Gender
        if 'GENDER' in df.columns:
            df['GENDER'] = df['GENDER'].str.upper()
            # Map variations to standard values
            gender_map = {
                'MALE': 'M',
                'FEMALE': 'F',
                'M': 'M',
                'F': 'F'
            }
            df['GENDER'] = df['GENDER'].map(gender_map).fillna('')
            
        # Ensure SYMPTOMS column is preserved and properly formatted
        if 'SYMPTOMS' in df.columns:
            df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
        else:
            print("Warning: SYMPTOMS column not found in input data")
        
        # Save the filtered data
        output_path = os.path.join('Upload_Folder', 'Filtered_Data.csv')
        df.to_csv(output_path, index=False)
        print(f"Total records in Filtered_Data.csv: {len(df)}")
        
        # Verify the output file
        if not os.path.exists(output_path):
            raise Exception("Failed to create Filtered_Data.csv")
            
        df_check = pd.read_csv(output_path)
        if df_check.empty:
            raise Exception("Filtered_Data.csv was created but contains no data")
            
        return True
        
    except Exception as e:
        print(f"Error in filterdata: {str(e)}")
        raise

def search(column):
    # More flexible pattern that looks for any mention of adverse effects related to covid vaccine
    pattern = r'.*(adverse|side|negative|complication|observed|-ve).*(covid|vaccine|vaccination)'
    try:
        res = re.search(pattern, str(column).lower())
        return bool(res)
    except Exception as e:
        print(f"Error in search function: {e}")
        return False

def adverseEffect():
    try:
        # Read the filtered data
        filtered_path = os.path.join('Upload_Folder', 'Filtered_Data.csv')
        if not os.path.exists(filtered_path):
            print("Error: Filtered_Data.csv not found. Please run filterdata() first.")
            return {}
            
        df = pd.read_csv(filtered_path)
        print(f"Total records in Filtered_Data.csv: {len(df)}")
        
        # Ensure SYMPTOMS column exists and is string type
        if 'SYMPTOMS' not in df.columns:
            print("Error: 'SYMPTOMS' column not found in Filtered_Data.csv")
            print("Available columns:", df.columns.tolist())
            return {}
            
        df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
        
        # Create new DataFrame for adverse effects
        df2 = pd.DataFrame(columns=df.columns)
        
        # Process each record
        for i in range(len(df)):
            symptoms = df.loc[i, 'SYMPTOMS']
            if search(symptoms):
                df2 = pd.concat([df2, pd.DataFrame([df.iloc[i]])], ignore_index=True)
                print(f"Found adverse effect in record {i}: {symptoms}")
        
        print(f"Total adverse effect records found: {len(df2)}")
        
        # Save to CSV
        output_path = os.path.join('Upload_Folder', 'AdverseEffect.csv')
        df2.to_csv(output_path, index=False)
        print(f"Saved adverse effects to: {output_path}")
        
        if len(df2) == 0:
            print("Warning: No adverse effects found in the data")
            
        return df2.to_dict()
        
    except Exception as e:
        print(f"Error in adverseEffect function: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {}

def efficacy():
    df=pd.read_csv('./Upload_Folder/extracted_data.csv')
    # df=data.drop(['Unnamed: 0'],axis=1)
    covid_count=len(df[df['Diagnosis'] == 'COVID +VE'])
    total_count=len(df)
    efficacy=(total_count-covid_count)/total_count*100
    return efficacy,covid_count
