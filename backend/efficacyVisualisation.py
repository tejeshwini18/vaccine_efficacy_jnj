import regex as re
def isSevere(str):
  severe=['breathing problem','chest pain','breathlessness']
  symList=str.split(', ')
  severeflag=0
  for item in symList:
      if item.lower() in severe:
          severeflag=1
  return severeflag
def getGender(df):
      df['PATIENT_GENDER'] = df['PATIENT_GENDER'].astype(str)
      df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
      df['DIAGNOSIS'] = df['DIAGNOSIS'].astype(str)
      gen=df['PATIENT_GENDER'].value_counts()
      male=int(gen['M'])
      female=int(gen['F'])
      M=[0,0,male]
      F=[0,0,female]
      for i in range(len(df)):
          gen=df.loc[i,'PATIENT_GENDER']
          sym=df.loc[i,'SYMPTOMS']
          covid=df.loc[i,'DIAGNOSIS']
          if(covid.lower()!='covid +ve'):
              continue
          severeflag=isSevere(sym)

          if(gen=='M'):
              M[0]+=1
              M[1]+=severeflag
          elif(gen=='F'):
              F[0]+=1
              F[1]+=severeflag
      dict={'M':M,'F':F}
      return dict

def getAge(df):
  df['PATIENT_AGE'] = df['PATIENT_AGE'].astype(int)
  df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
  df['DIAGNOSIS'] = df['DIAGNOSIS'].astype(str)
  age18=[0,0,0]
  age31=[0,0,0]
  age41=[0,0,0]
  age51=[0,0,0]
  age61=[0,0,0]
  age71=[0,0,0]
  age81=[0,0,0]
  age91=[0,0,0]
  

  for i in range(len(df)):
      covid=df.loc[i,'DIAGNOSIS']
      age=df.loc[i,'PATIENT_AGE']
      sym=df.loc[i,'SYMPTOMS']
      severeflag=isSevere(sym)
      if((age>=18) and (age<=30)):
          age18[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age18[0]+=1
          age18[1]+=severeflag
    
      if((age>=31) and (age<=40)):
        age31[2]+=1
        if(covid.lower()!='covid +ve'):
            continue
        age31[0]+=1
        age31[1]+=severeflag
      if((age>=41) and (age<=50)):
          age41[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age41[0]+=1
          age41[1]+=severeflag
      if((age>=51) and (age<=60)):
          age51[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age51[0]+=1
          age51[1]+=severeflag
      if((age>=61) and (age<=70)):
          age61[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age61[0]+=1
          age61[1]+=severeflag

      elif((age>=71) and (age<=80)):
          age71[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age71[0]+=1
          age71[1]+=severeflag

      elif((age>=81) and (age<=90)):
          age81[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age81[0]+=1
          age81[1]+=severeflag

      elif((age>=91) and (age<=100)):
          age91[2]+=1
          if(covid.lower()!='covid +ve'):
            continue
          age91[0]+=1
          age91[1]+=severeflag
  dict={'18-30':age18,'31-40':age31,'41-50':age41,'51-60':age51,'61-70':age61,'71-80':age71,'81-90':age81,'91-100':age91}
  return dict

def getQuarter(df):
    df['DATE_OF_VISIT'] = df['DATE_OF_VISIT'].astype(str)
    df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
    df['DIAGNOSIS'] = df['DIAGNOSIS'].astype(str)
    q1=[0,0,0]
    q2=[0,0,0]
    q3=[0,0,0]
    q4=[0,0,0]
    for i in range(len(df)):
        covid=df.loc[i,'DIAGNOSIS']
        dov=df.loc[i,'DATE_OF_VISIT']
        sym=df.loc[i,'SYMPTOMS']
        
        severeflag=isSevere(sym)
        temp1=re.findall(r'/\d{0,2}/',dov)[0]
        temp2=re.findall(r'\d{0,2}',temp1)[1]
        temp2=int(temp2)
        if(temp2<=3):
            q1[2]+=1
            if(covid.lower()!='covid +ve'):
                continue
            q1[0]+=1
            q1[1]+=severeflag
        if(temp2<=6 and temp2>3):
            q2[2]+=1
            if(covid.lower()!='covid +ve'):
                continue
            q2[0]+=1
            q2[1]+=severeflag
        if(temp2<=9 and temp2>6):
            q3[2]+=1
            if(covid.lower()!='covid +ve'):
                continue
            q3[0]+=1
            q3[1]+=severeflag
        elif(temp2>9 and temp2<=12):
            q4[2]+=1
            if(covid.lower()!='covid +ve'):
                continue
            q4[0]+=1
            q4[1]+=severeflag
    dict={'Q1 2021':q1,'Q2 2021':q2,'Q3 2021':q3,'Q4 2021':q4}
    return dict

def getSymptoms(df):
    coviddf=df[df['DIAGNOSIS']=='COVID +VE']
    symp=coviddf.SYMPTOMS.str.split(', ',expand=True).stack().value_counts()
    symp1=symp.head(10)
    symp_dict=symp1.to_dict()
    symp_dict.pop("nan")
    return symp_dict