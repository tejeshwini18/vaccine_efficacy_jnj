# Save results to CSV
import pandas as pd
import os

UPLOAD_FOLDER = './Upload_Folder'
df = pd.read_csv('Upload_Folder/extracted_data.csv')


# Create a new DataFrame with only SYMPTOMS column
df_symptoms = df[['SYMPTOMS']].copy()

# Save the filtered data
df_symptoms.to_csv(os.path.join(UPLOAD_FOLDER, 'AdverseEffect.csv'), index=False)

print(f"Adverse effects data saved to: {os.path.join(UPLOAD_FOLDER, 'AdverseEffect.csv')}")
print(f"Total number of symptom records: {len(df_symptoms)}")