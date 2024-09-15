from email import message
from flask import Flask,render_template, request,redirect, url_for, send_file
import zipfile
from werkzeug.utils import secure_filename
import os
import extractionPrinceton
import analysis
import adverseVisualisation as av
import efficacyVisualisation as ev
import json
import io
import base64
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

app = Flask(__name__)

fig,ax = plt.subplots(figsize=(6,6))
ax = sns.set_style(style='darkgrid')

x = [i for i in range(100)]
y = [i for i in range(100)]


@app.route('/')
def hello():
  return {'hi':1,'bye':2}


@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method=="POST":
      print(request.files)
      f=request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join('UploadFolder',filename))
      path='./UploadFolder/'+filename
      print(filename)      
      with zipfile.ZipFile(path,"r") as zip_ref:
        zip_ref.extractall('./UploadFolder')
      extractionPrinceton.extract()
      covid=analysis.filterdata()
      adverse=analysis.adverseEffect()
      return covid
    return "Failed"

@app.route('/downloadFiltered')
def downloadFiltered():
    path = r"C:\Users\1945686\OneDrive - TCS COM PROD\EHR Rest\Backend\Updated_Main.csv"
    return send_file(path, as_attachment=True)


@app.route('/downloadAdverse')
def downloadAdverse():
  path = r"C:\Users\1945686\OneDrive - TCS COM PROD\EHR Rest\Backend\AdverseEffect1.csv"
  return send_file(path, as_attachment=True)


@app.route("/efficacy")
def efficacy():
  data1 = pd.read_csv('Updated_Main.csv')
  data2=pd.read_csv('Updated_Main.csv')
  data2['SYMPTOMS']=data2['SYMPTOMS'].str.lower()

  age_dict = ev.getAge(data2)
  gen_dict = ev.getGender(data2)
  symp_dict = ev.getSymptoms(data2)
  quarter_dict=ev.getQuarter(data2)

  data = {
    'age':age_dict,
    'gen':gen_dict,
    'sym':symp_dict,
    'quat':quarter_dict,
  }
  return data

@app.route("/adverseEffect")
def adverse():
  data1 = pd.read_csv('Updated_Main.csv')
  data2=pd.read_csv('AdverseEffect1.csv')
  count2 = len(data2)
  data2['DIAGNOSIS']=data2['DIAGNOSIS'].str.lower()
  data2['SYMPTOMS']=data2['SYMPTOMS'].str.lower()
  data2['OBSERVATION']=data2['OBSERVATION'].str.lower()
  age_dict = av.getAge(data2,data1)
  gen_dict = av.getGender(data2,data1)
  symp_dict = av.getSymptoms(data2)

  data = {
    'age':age_dict,
    'gen':gen_dict,
    'symp':symp_dict,
  }
  return data

@app.route('/efficacycount')
def efficacycount():
  data1 = pd.read_csv('Updated_Main.csv')
  vaccinatedCount = len(data1)
  data2=pd.read_csv('AdverseEffect1.csv')
  adverse = len(data2)
  totalData=4550

  efficacy,covidCount=analysis.efficacy()
  adversePercent=round((adverse/vaccinatedCount)*100, 2)
  efficacy=str(round(efficacy, 2))+'%'
  data={
    'Total Prescriptions':totalData,
    'Vaccinated Count (J&J)':vaccinatedCount,
    'Post Vaccination Covid Cases':covidCount,
    'Overall Vaccine Efficacy (J&J)':efficacy,  
  }
  return data

@app.route('/adversecount')
def adversecount():
  data1 = pd.read_csv('Updated_Main.csv')
  vaccinatedCount = len(data1)
  data2=pd.read_csv('AdverseEffect1.csv')
  adverse = len(data2)
  totalData=4550

  efficacy,covidCount=analysis.efficacy()
  adversePercent=str(round((adverse/vaccinatedCount)*100, 2))+'%'
  efficacy=round(efficacy, 2)
  data={
    'Total Prescriptions':totalData,
    'Vaccinated Count (J&J)':vaccinatedCount,
    'Post Vaccination Adverse Effect Cases':adverse,
    'Adverse Effect Percentage':adversePercent,     
  }
  return data


if __name__ == "__main__":
  app.run(debug=True)