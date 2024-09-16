from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify  # Correct import
import zipfile
from werkzeug.utils import secure_filename
import os
import zipped_extraction
import analysis
import adverseVisualisation as av
import efficacyVisualisation as ev
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Status variable
processing_status = {
    'status': 'not_started'  # Default status
}

# Ensure the UploadFolder exists
UPLOAD_FOLDER = 'Upload_Folder'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home route
@app.route('/')
def hello():
    return {'hi': 1, 'bye': 2}

# Upload Route
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        try:
            global processing_status
            processing_status['status'] = 'processing'
            f = request.files['file']
            filename = secure_filename(f.filename)
            file_path = os.path.join('Upload_Folder', filename)
            f.save(file_path)
            # Process the uploaded zip file
            output_csv = zipped_extraction.process_uploaded_files(file_path)
            processing_status['status'] = 'completed'
            return send_file(output_csv, as_attachment=True)
        
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return "Upload failed", 400


# Download filtered data CSV
@app.route('/downloadFiltered')
def downloadFiltered():
    ev.filterdata()
    path = os.path.join(UPLOAD_FOLDER, "Filtered_Data.csv")
    return send_file(path, as_attachment=True)

# Download adverse effect CSV
@app.route('/downloadAdverse')
def downloadAdverse():
    ev.adverseEffect()
    path = os.path.join(UPLOAD_FOLDER, "AdverseEffect.csv")
    return send_file(path, as_attachment=True)

# Efficacy analysis route
@app.route("/efficacy")
def efficacy():
    data2 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    data2['SYMPTOMS'] = data2['SYMPTOMS'].str.lower()

    age_dict = ev.getAge(data2)
    gen_dict = ev.getGender(data2)
    symp_dict = ev.getSymptoms(data2)
    quarter_dict = ev.getQuarter(data2)

    data = {
        'age': age_dict,
        'gen': gen_dict,
        'sym': symp_dict,
        'quat': quarter_dict,
    }
    return jsonify(data)  # Ensure return is JSON

# Adverse Effect analysis route
@app.route("/adverseEffect")
def adverse():
    data1 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    data2 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'AdverseEffect1.csv'))

    data2['DIAGNOSIS'] = data2['DIAGNOSIS'].str.lower()
    data2['SYMPTOMS'] = data2['SYMPTOMS'].str.lower()
    data2['OBSERVATION'] = data2['OBSERVATION'].str.lower()

    age_dict = av.getAge(data2, data1)
    gen_dict = av.getGender(data2, data1)
    symp_dict = av.getSymptoms(data2)

    data = {
        'age': age_dict,
        'gen': gen_dict,
        'symp': symp_dict,
    }
    return jsonify(data)  # Ensure return is JSON

# Efficacy count route
@app.route('/efficacycount')
def efficacycount():
    data1 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    vaccinatedCount = len(data1)

    efficacy, covidCount = analysis.efficacy()
    efficacy = str(round(efficacy, 2)) + '%'

    data = {
        'Vaccinated Count (J&J)': vaccinatedCount,
        'Post Vaccination Covid Cases': covidCount,
        'Overall Vaccine Efficacy (J&J)': efficacy,
    }
    return jsonify(data)  # Ensure return is JSON

# Adverse effect count route
@app.route('/adversecount')
def adversecount():
    data1 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    vaccinatedCount = len(data1)

    data2 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'AdverseEffect1.csv'))
    adverse = len(data2)

    adversePercent = str(round((adverse / vaccinatedCount) * 100, 2)) + '%'
    efficacy, covidCount = analysis.efficacy()

    data = {
        'Vaccinated Count (J&J)': vaccinatedCount,
        'Post Vaccination Adverse Effect Cases': adverse,
        'Adverse Effect Percentage': adversePercent,
    }
    return jsonify(data)  # Ensure return is JSON

@app.route('/gender-distribution')
def gender_distribution():
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    df2 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'AdverseEffect1.csv'))
    img_str = av.plot_gender_distribution(df, df2)
    return jsonify({'image': img_str})

@app.route('/age-distribution')
def age_distribution():
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    df2 = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'AdverseEffect1.csv'))
    img_str = av.plot_age_distribution(df, df2)
    return jsonify({'image': img_str})

@app.route('/symptom-distribution')
def symptom_distribution():
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv'))
    img_str = av.plot_symptom_distribution(df)
    return jsonify({'image': img_str})

@app.route('/processing-status', methods=['GET'])
def get_processing_status():
    return jsonify(processing_status)  # Ensure return is JSON

if __name__ == "__main__":
    app.run(debug=True)