from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
import zipfile
from werkzeug.utils import secure_filename
import os
from new_backend import zipped_extraction
from new_backend import analysis
from new_backend import adverseVisualisation as av
from new_backend import efficacyVisualisation as ev
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key'  # Required for flashing messages

processing_status = {'status': 'not_started', 'message': ''}

UPLOAD_FOLDER = './Upload_Folder'
ALLOWED_EXTENSIONS = {'zip'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        try:
            global processing_status
            processing_status['status'] = 'processing'
            processing_status['message'] = 'Starting file upload...'
            
            # Check if file was uploaded
            if 'file' not in request.files:
                processing_status['status'] = 'error'
                processing_status['message'] = 'No file uploaded'
                return jsonify({'error': 'No file uploaded'}), 400
                
            f = request.files['file']
            if f.filename == '':
                processing_status['status'] = 'error'
                processing_status['message'] = 'No file selected'
                return jsonify({'error': 'No file selected'}), 400
                
            # Check if file is a ZIP
            if not f.filename.endswith('.zip'):
                processing_status['status'] = 'error'
                processing_status['message'] = 'File must be a ZIP file'
                return jsonify({'error': 'File must be a ZIP file'}), 400
            
            # Save the uploaded file
            filename = secure_filename(f.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            f.save(file_path)
            processing_status['message'] = 'File saved, starting extraction...'
            
            # Process the ZIP file
            try:
                output_csv = zipped_extraction.process_uploaded_files(file_path)
                processing_status['status'] = 'completed'
                processing_status['message'] = 'File processed successfully'
                
                # Return success response with file paths
                return jsonify({
                    'message': 'File processed successfully',
                    'files': {
                        'extracted_data': 'extracted_data.csv',
                        'filtered_data': 'Filtered_Data.csv',
                        'adverse_effects': 'AdverseEffect.csv'
                    }
                })
                
            except Exception as e:
                processing_status['status'] = 'error'
                processing_status['message'] = f'Error processing file: {str(e)}'
                return jsonify({'error': str(e)}), 500
                
        except Exception as e:
            processing_status['status'] = 'error'
            processing_status['message'] = f'An error occurred: {str(e)}'
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid request method'}), 400

@app.route('/downloadFiltered')
def downloadFiltered():
    try:
        # First check if extracted_data.csv exists
        extracted_path = os.path.join(UPLOAD_FOLDER, "extracted_data.csv")
        if not os.path.exists(extracted_path):
            return jsonify({'error': 'No data available. Please upload and process the ZIP file first.'}), 404

        # Generate filtered data
        ev.filterdata()
        
        # Check if filtered data was created
        filtered_path = os.path.join(UPLOAD_FOLDER, "Filtered_Data.csv")
        if not os.path.exists(filtered_path):
            return jsonify({'error': 'Failed to generate filtered data. Please try again.'}), 500
            
        # Verify the file has content
        df = pd.read_csv(filtered_path)
        if df.empty:
            return jsonify({'error': 'No data available in filtered file.'}), 404
            
        return send_file(filtered_path, as_attachment=True, download_name="Filtered_Data.csv")
    except Exception as e:
        print(f"Error in downloadFiltered: {str(e)}")
        return jsonify({'error': f'Error downloading filtered data: {str(e)}'}), 500

@app.route('/downloadAdverse')
def downloadAdverse():
    try:
        # Check if adverse effects data exists
        adverse_path = os.path.join(UPLOAD_FOLDER, "AdverseEffect.csv")
        print(f"Checking for adverse effects file at: {adverse_path}")
        
        if not os.path.exists(adverse_path):
            print("Adverse effects file not found")
            return jsonify({'error': 'No adverse effects data available. Please upload and process the ZIP file first.'}), 404

        # Verify the file has content
        df = pd.read_csv(adverse_path)
        print(f"Found {len(df)} records in adverse effects file")
        
        if df.empty:
            print("Adverse effects file is empty")
            return jsonify({'error': 'No adverse effects found in the data.'}), 404
            
        print("Sending adverse effects file for download")
        return send_file(adverse_path, as_attachment=True, download_name="AdverseEffect.csv")
    except Exception as e:
        print(f"Error in downloadAdverse: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Error downloading adverse effects data: {str(e)}'}), 500

@app.route("/efficacy")
def efficacy():
    main_path = os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv')
    if not os.path.exists(main_path):
        return jsonify({'error': 'Updated_Main.csv not found. Please upload and process the ZIP file first.'}), 404
    
    data2 = pd.read_csv(main_path)
    data2['SYMPTOMS'] = data2['SYMPTOMS'].str.lower()

    age_dict = ev.getAge(data2)
    gen_dict = ev.getGender(data2)
    symp_dict = ev.getSymptoms(data2)
    quarter_dict = ev.getQuarter(data2)

    return jsonify({
        'age': age_dict,
        'gen': gen_dict,
        'sym': symp_dict,
        'quat': quarter_dict,
    })

@app.route("/adverseEffect")
def adverse():
    main_path = os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv')
    adverse_path = os.path.join(UPLOAD_FOLDER, 'AdverseEffect.csv')

    if not os.path.exists(main_path) or not os.path.exists(adverse_path):
        return jsonify({'error': 'Required files not found. Please upload and process the ZIP file first.'}), 404

    data1 = pd.read_csv(main_path)
    data2 = pd.read_csv(adverse_path)

    data2['DIAGNOSIS'] = data2['DIAGNOSIS'].str.lower()
    data2['SYMPTOMS'] = data2['SYMPTOMS'].str.lower()
    data2['OBSERVATION'] = data2['OBSERVATION'].str.lower()

    age_dict = av.getAge(data2, data1)
    gen_dict = av.getGender(data2, data1)
    symp_dict = av.getSymptoms(data2)

    return jsonify({
        'age': age_dict,
        'gen': gen_dict,
        'symp': symp_dict,
    })

@app.route('/efficacycount')
def efficacycount():
    main_path = os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv')
    if not os.path.exists(main_path):
        return jsonify({'error': 'Updated_Main.csv not found. Please upload and process the ZIP file first.'}), 404

    data1 = pd.read_csv(main_path)
    vaccinatedCount = len(data1)

    efficacy, covidCount = analysis.efficacy()
    efficacy = str(round(efficacy, 2)) + '%'

    return jsonify({
        'Vaccinated Count (J&J)': vaccinatedCount,
        'Post Vaccination Covid Cases': covidCount,
        'Overall Vaccine Efficacy (J&J)': efficacy,
    })

@app.route('/adversecount')
def adversecount():
    main_path = os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv')
    adverse_path = os.path.join(UPLOAD_FOLDER, 'AdverseEffect.csv')

    if not os.path.exists(main_path) or not os.path.exists(adverse_path):
        return jsonify({'error': 'Required files not found. Please upload and process the ZIP file first.'}), 404

    data1 = pd.read_csv(main_path)
    data2 = pd.read_csv(adverse_path)

    vaccinatedCount = len(data1)
    adverse = len(data2)

    adversePercent = str(round((adverse / vaccinatedCount) * 100, 2)) + '%'
    efficacy, covidCount = analysis.efficacy()

    return jsonify({
        'Vaccinated Count (J&J)': vaccinatedCount,
        'Post Vaccination Adverse Effect Cases': adverse,
        'Adverse Effect Percentage': adversePercent,
    })

@app.route('/gender-distribution')
def gender_distribution():
    main_path = os.path.join(UPLOAD_FOLDER, 'Filtered_Data.csv')
    adverse_path = os.path.join(UPLOAD_FOLDER, 'extracted_data.csv')

    if not os.path.exists(main_path) or not os.path.exists(adverse_path):
        return jsonify({'error': 'Required files not found. Please upload and process the ZIP file first.'}), 404

    df = pd.read_csv(main_path)
    df2 = pd.read_csv(adverse_path)
   
    img_str = av.plot_gender_distribution(df, df2)
    return jsonify({'image': img_str})

@app.route('/age-distribution')
def age_distribution():
    main_path = os.path.join(UPLOAD_FOLDER, 'Filtered_Data.csv')
    adverse_path = os.path.join(UPLOAD_FOLDER, 'extracted_data.csv')

    if not os.path.exists(main_path) or not os.path.exists(adverse_path):
        return jsonify({'error': 'Required files not found. Please upload and process the ZIP file first.'}), 404

    df = pd.read_csv(main_path)
    df2 = pd.read_csv(adverse_path)
    img_str = av.plot_age_distribution(df, df2)
    return jsonify({'image': img_str})

@app.route('/symptom-distribution')
def symptom_distribution():
    main_path = os.path.join(UPLOAD_FOLDER, 'Updated_Main.csv')
    if not os.path.exists(main_path):
        return jsonify({'error': 'Updated_Main.csv not found. Please upload and process the ZIP file first.'}), 404

    df = pd.read_csv(main_path)
    img_str = av.plot_symptom_distribution(df)
    return jsonify({'image': img_str})

@app.route('/processing-status', methods=['GET'])
def get_processing_status():
    return jsonify(processing_status)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                zipped_extraction.process_uploaded_files(filepath)
                flash('File processed successfully!')
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
            return redirect(url_for('upload_file'))
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
