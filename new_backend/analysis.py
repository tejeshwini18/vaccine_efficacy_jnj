import pandas as pd
import os

def efficacy():
    """
    Calculate vaccine efficacy based on the data in Updated_Main.csv
    Returns:
        tuple: (efficacy percentage, number of covid cases)
    """
    main_path = os.path.join('Upload_Folder', 'Updated_Main.csv')
    if not os.path.exists(main_path):
        raise FileNotFoundError("Updated_Main.csv not found")
    
    data = pd.read_csv(main_path)
    total_vaccinated = len(data)
    covid_cases = len(data[data['SYMPTOMS'].str.contains('covid', case=False, na=False)])
    
    if total_vaccinated == 0:
        return 0, 0
        
    efficacy = ((total_vaccinated - covid_cases) / total_vaccinated) * 100
    return efficacy, covid_cases 