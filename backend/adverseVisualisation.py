def isSevere(str):
  severe=['breathing problem','chest pain','breathlessness']
  symList=str.split(', ')
  severeflag=0
  for item in symList:
      if item.lower() in severe:
          severeflag=1
  return severeflag
def getGender(df,df2):
      df['PATIENT_GENDER'] = df['PATIENT_GENDER'].astype(str)
      df2['PATIENT_GENDER'] = df2['PATIENT_GENDER'].astype(str)
      df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
      M=[0,0,0]
      F=[0,0,0]
      for i in range(len(df2)):
        gen=df2.loc[i,'PATIENT_GENDER']
        if(gen=='M'):
            M[2]+=1
        elif(gen=='F'):
            F[2]+=1

      for i in range(len(df)):
          gen=df.loc[i,'PATIENT_GENDER']
          sym=df.loc[i,'SYMPTOMS']
          severeflag=isSevere(sym)

          if(gen=='M'):
              M[0]+=1
              M[1]+=severeflag
          if(gen=='F'):
              F[0]+=1
              F[1]+=severeflag
      dict={'M':M,'F':F}
      return dict

def getAge(df,df2):
  df['PATIENT_AGE'] = df['PATIENT_AGE'].astype(int)
  df2['PATIENT_AGE'] = df2['PATIENT_AGE'].astype(int)
  df['SYMPTOMS'] = df['SYMPTOMS'].astype(str)
  age18=[0,0,0]
  age31=[0,0,0]
  age41=[0,0,0]
  age51=[0,0,0]
  age61=[0,0,0]
  age71=[0,0,0]
  age81=[0,0,0]
  age91=[0,0,0]
  for i in range(len(df2)):
    age=df2.loc[i,'PATIENT_AGE']
    if((age>=18) and (age<=30)):
        age18[2]+=1
    elif((age>=31) and (age<=40)):
        age31[2]+=1
    elif((age>=41) and (age<=50)):
        age41[2]+=1
    elif((age>=51) and (age<=60)):
        age51[2]+=1
    elif((age>=61) and (age<=70)):
        age61[2]+=1
    elif((age>=71) and (age<=80)):
        age71[2]+=1
    elif((age>=81) and (age<=90)):
        age81[2]+=1
    elif((age>=91) and (age<=100)):
        age91[2]+=1
  for i in range(len(df)):
      age=df.loc[i,'PATIENT_AGE']
      sym=df.loc[i,'SYMPTOMS']
      
      severeflag=isSevere(sym)
      if((age>=18) and (age<=30)):
          age18[0]+=1
          age18[1]+=severeflag
    
      elif((age>=31) and (age<=40)):
        age31[0]+=1
        age31[1]+=severeflag
      elif((age>=41) and (age<=50)):
          age41[0]+=1
          age41[1]+=severeflag
      elif((age>=51) and (age<=60)):
          age51[0]+=1
          age51[1]+=severeflag
      elif((age>=61) and (age<=70)):
          age61[0]+=1
          age61[1]+=severeflag

      elif((age>=71) and (age<=80)):
          age71[0]+=1
          age71[1]+=severeflag

      elif((age>=81) and (age<=90)):
          age81[0]+=1
          age81[1]+=severeflag

      elif((age>=91) and (age<=100)):
          age91[0]+=1
          age91[1]+=severeflag
  dict={'18-30':age18,'31-40':age31,'41-50':age41,'51-60':age51,'61-70':age61,'71-80':age71,'81-90':age81,'91-100':age91}
  return dict

def getSymptoms(df):
    symp=df.SYMPTOMS.str.split(', ',expand=True).stack().value_counts()
    symp1=symp.head(10)
    symp_dict=symp1.to_dict()
    symp_dict.pop("adverse effect of covid vaccine")
    symp_dict.pop("nan")
    return symp_dict