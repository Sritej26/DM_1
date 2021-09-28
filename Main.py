# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 14:42:05 2021

@author: Sritej. N
"""

import pandas as pd
import datetime

insulin_data=pd.read_csv("InsulinData.csv")
insulin_data=insulin_data.drop(['Index'], axis=1)
insulin_data['Date']=pd.to_datetime(insulin_data['Date'], format="%m/%d/%Y")
insulin_data['Time'] = pd.to_timedelta(insulin_data['Time'])

InSearchOfAutoMode = pd.DataFrame((insulin_data.loc[insulin_data['Alarm'] == 'AUTO MODE ACTIVE PLGM OFF']))
InSearchOfAutoMode=InSearchOfAutoMode.sort_values(by=['Date'],ascending=True)

AutoM_Start_Date=InSearchOfAutoMode.iloc[0]['Date']
AutoM_Start_Time=InSearchOfAutoMode.iloc[0]['Time']

cgm_data=pd.read_csv("CGMData.csv").drop(['Index'],axis=1)
cgm_data['Date']=pd.to_datetime(cgm_data['Date'], format="%m/%d/%Y")
cgm_data['Time'] = pd.to_timedelta(cgm_data['Time'])

cgm_data = cgm_data[["Date", "Time", "Sensor Glucose (mg/dL)"]]

NightStart = datetime.timedelta(hours=0, minutes=0, seconds=0)
DayStart = datetime.timedelta(hours=6, minutes=0, seconds=0)
NightEnd = datetime.timedelta(hours=5, minutes=59, seconds=59)
DayEnd = datetime.timedelta(hours=23, minutes=59, seconds=59)



def getDayorNight (time):
    if time >= NightStart and time <= NightEnd:
        return 'overnight'
    elif time >= DayStart and time <= DayEnd:
        return 'daytime'
    else:
        return 0



cgm_timeCategory = pd.DataFrame()
cgm_timeCategory['time_Category'] = cgm_data.apply(lambda row: getDayorNight(row['Time']), axis=1)

cgm_data=cgm_data.join(cgm_timeCategory)



def compare(df,level):
    s=0
    if(level==1):
        s=df[df['Sensor Glucose (mg/dL)']>180].shape[0]
    elif(level==2):
        s=df[df['Sensor Glucose (mg/dL)']>250].shape[0]
    elif(level==3):
        s=df[(df['Sensor Glucose (mg/dL)']>=70) & (df['Sensor Glucose (mg/dL)']<=180) ].shape[0]
    elif(level==4):
        s=df[(df['Sensor Glucose (mg/dL)']>=70) & (df['Sensor Glucose (mg/dL)']<=150) ].shape[0]
    elif(level==5):
        s=df[df['Sensor Glucose (mg/dL)']<70].shape[0]
    elif(level==6):
        s=df[df['Sensor Glucose (mg/dL)']<54].shape[0]
    
    return s


def getMetrix(level,mode,Time_category):
    dates_unique=mode['Date'].unique()
    s=0
    if(Time_category=='overnight' or Time_category=='daytime'):       
        for d in dates_unique:
            daylist=mode[(mode['Date']==d) & (mode['time_Category']==Time_category)]
            s+=(compare(daylist,level)/288.)*100
        s=s/len(dates_unique)
            
    elif(Time_category=='wholeday'):
        for d in dates_unique:
            daylist=mode[mode['Date']==d ]
            s+=(compare(daylist,level)/288.)*100
        s=s/len(dates_unique)
    return s
    
def getmode (date, time):
    if date <AutoM_Start_Date :
        return 'Manual'
    elif date == AutoM_Start_Date:
        if time < AutoM_Start_Time:
            return 'Manual'
        else:
            return 'Auto'
    else:
        return 'Auto'
cgm_mode=pd.DataFrame()
cgm_mode['mode'] = cgm_data.apply(lambda row: getmode(row['Date'], row['Time']), axis=1)

cgm_data = cgm_data.join(cgm_mode)
cgm_data = cgm_data.reset_index(drop=True)


cgm_m=cgm_data[cgm_data['mode']=='Manual']
cgm_m=cgm_m.reset_index(drop=True)

cgm_a=cgm_data[cgm_data['mode']=='Auto']
cgm_a=cgm_a.reset_index(drop=True)

manual_values=[]
t_category=['overnight','daytime','wholeday']

for i in t_category:
    for j in range(1,7):
        manual_values.append(getMetrix(j,cgm_m,i))
        
manual_values.append(1.1)
auto_values=[]
for i in t_category:
    for j in range(1,7):
        auto_values.append(getMetrix(j,cgm_a,i))

auto_values.append(1.1)

metrics = pd.DataFrame(list(zip(manual_values, auto_values)))
    
metrics=metrics.transpose()  
metrics.to_csv("Results.csv",index=False,header=False)














