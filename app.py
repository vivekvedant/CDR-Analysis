
"""
Challenges in the raw CDR data needed to handled or processed

1. No column name   
   ( header = None )
    column no -  actual name
    1            serviceProvider
    5            direction
    9            startTime
    13           EndTime
    120          userId 
    180          twoStageDialingDigits
    146          relatedCallId
    147          relatedCallIdReason
    267          vpDialingfacResult
    312          locationType
    345          userAgent


2 . Columns (6,8,20,29,69,71,73,75,77,99,119,126,133,134,148,152,
         174,179,181,194,195,196,200,274,304,307,313,
         319,346,409,412,434,442) have mixed types
    ( lowmemory = false )

3. Column 9 and 13 contains date and time information in regular pattern like- 
    "20190620032717.906". col 9 - start date and col 13 - end date
    First 8 characters represents Date
    Rest characters represents Time
    2019 year, 06 month, 20 day, 03 hours, 27 minutes, 17 sec
    ( function datetime_divider )
    
4. Column 5, 267, 312 contains a simple name for a Standard Terminologies

5. Column 312 conatins some unmwanted data other than the main data in it

6. Column 147 contains all the services/feature offered but some services are
    also distributed among column 267, 312 which are needed to be in col 147.
    
7. No information about the start and end of the call and total duration of the
    call

8. No hour wise distribution and week wise distribution of the calls 
    
"""

import pandas as pd
import re
import numpy as np
import datetime



df = pd.read_csv("raw_cdr_data.csv",header = None,low_memory = False)

def datetime_div(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))):
            regex = re.compile("\d{1,8}")
            string_split = regex.findall(str(data[index]))
            data[index] = [ string_split[0] , string_split[1]]
        else:
            data[index] = [np.nan,np.nan]
    return data
    
    
data = ["20190620032717.906", "20190620052652.52",'' ,"20190620052735.207"]    
# date = datetime_div(data)
date,time = zip(*datetime_div(data))


def date_modifier(data):
  for index in range(len(data)):
      if(re.match("^\d",str(data[index]))):
          year = data[index][:4]
          month = data[index][4:6]
          date = data[index][6:]
          data[index] = "-".join([year,month,date])
      else:
          data[index] = np.nan
  return data

result = date_modifier(list(date))
# print(result)

def time_modifier(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))):
            hours = int(data[index][:2])
            minutes=  data[index][2:4]
            seconds = data[index][4:]
            
            if(hours >= 12):
                if(hours == 12):
                    hr = str(hours)
                else:
                    hr = str(hours - 12)
                
                meridiem = "PM"
                
            else:
               if(hours == 0):
                   hr = str(12)
               else:
                   hr = str(hours)
               meridiem = "AM"
            data[index] = ":".join([hr,minutes,seconds])+" " + meridiem
        
        else:
            data[index]= np.nan
            
    return data     
    
    
result = time_modifier(list(time))


def replace_simple_with_Standard_terminology(dataframe):
    # This part replace the data with standard terminologies in col 5, 267, 312
    # Replacing String in the columns with standard Terminology
    dataframe[5] = dataframe[5].replace("Originating", "Outgoing")
    dataframe[5] = dataframe[5].replace("Terminating", "Incoming")
    
    dataframe[267] = dataframe[267].replace("Success", "Voice Portal")

    dataframe[312] = dataframe[312].replace("Shared Call Appearance", "Secondary Device")
    
    return dataframe


def remove_Unwanted_data(datacolumn):
    # data type of data is list
    for index in range(len(datacolumn)):
        if datacolumn[index] == "Secondary Device" or datacolumn[index] =="Primary Device":
            continue
        else:
            datacolumn[index] = np.nan 
    return datacolumn



def combine_all_servies(datacolumn147,datacolumn312,datacolumn267):
    for index in range(len(datacolumn147)):
        if datacolumn147[index] is  np.nan:
            if(datacolumn267[index] is not np.nan) and (datacolumn312[index] is not np.nan):
                datacolumn147[index] = str(datacolumn312[index]) + "," + str(datacolumn267[index])
            elif datacolumn312[index] is not np.nan:
                datacolumn147[index] = datacolumn312[index]
            else:
                datacolumn147[index] = datacolumn267[index]
        else:
            continue
    return datacolumn147



    

data1 = ['Primary Device','Simultaneous Ring Personal', 'Secondary Device','Remote Office', 'Simultaneous Ring Personal']
data2 = ['Primary Device', 'Secondary Device','Primary Device', 'Secondary Device', 'Primary Device']    
data3 = ['Voice Portal']
result = combine_all_servies(data1,data2,data3)
print(result)


def call_time_fetcher(data):

    for index in range(len(data)):
        data[index] = str(data[index])
        if data[index]!="nan":
            year = data[index][:4]
            month = data[index][4:6]
            day = data[index][6:8]
            hours = data[index][8:10]
            minutes = data[index][10:12]
            seconds = str(round(float(data[index][12:])))
            if int(seconds) >= 60:
                seconds = int(seconds) -60
                minutes = int(minutes)+1 
            if int(minutes) >=60:
                hours = int(hours)+1
                minutes  = int(minutes) - 60 
            data[index] = f"{year}-{month}-{day} {hours}:{minutes}:{seconds}"
        else:
            data[index] = np.nan
    return data


data = ["20190620032717.906", "20190620052652.52",'nan' ,"20190620052735.207"]
result = call_time_fetcher (data)
print(result)


def hourly_range(data):
    # Time column data is passed as a list
    # 03:27:17 AM'
    for index in range(len(data)):
        data[index] = str(data[index])
        if data[index]!="nan":
            if re.search("PM", data[index]):
                time_data =  re.findall("\d+", data[index])
                if time_data[0] != "12":
                    time_data = int(time_data[0]) + 12
                else:
                    time_data = time_data[0]
                
            else:
                time_data =  re.findall("\d+", data[index])
                if int(time_data[0]) == 12:
                    time_data = f"0{int(time_data[0]) - 12}"
                else:
                    time_data = time_data[0]
                
                
            data[index] = f"{time_data}:00 - {time_data}:59"
        else:
            data[index] = np.nan
    return data

converted_time_dummy = ['03:27:17 AM', '05:26:52 AM', 'nan', ':0:0 PM']
result = hourly_range(converted_time_dummy)
print(result)



def weekly_range(data):
    # Date column data is passed as a list
    # '2019-06-20' 
    for index in range(len(data)):
        data[index] = str(data[index])
        if data[index] != "nan":
            year, month, day = [int(x) for x in data[index].split("-")]
            result = datetime.date(year, month, day)
            data[index] = result.strftime("%A")
        else:
            data[index] = np.nan
    return data

date_dummy= ['2019-06-20', '2019-06-20', 'nan', '2019-06-20']
result = weekly_range(date_dummy)
print(result)




df['date'],df['time'] = zip(*datetime_div(df[9].tolist()))

df['date'] = date_modifier(df['date'].tolist())
df['time'] = time_modifier(df['time'].tolist())



df = replace_simple_with_Standard_terminology(df)


df[312] = remove_Unwanted_data(df[312])

print(df[312].unique())

df[147] = combine_all_servies(df[147].tolist(),df[312].tolist(),df[267].tolist())

print(df[147].unique())

df['starttime'] = pd.to_datetime(call_time_fetcher(df[9].tolist()))
print(df['starttime'])

df['endtime'] = pd.to_datetime(call_time_fetcher(df[13].tolist()))
print(df['endtime'])

df['duration'] = (df['endtime'] - df['starttime']).astype("timedelta64[m]")
print(df['duration'])

df['hourly_range'] = hourly_range(df['time'].tolist())
print(df['hourly_range'])


df['weekly_range'] = weekly_range(df['date'].tolist())
print(df['weekly_range'])



df.drop("time",axis = 1,inplace = True)
df.to_csv("cdr_data.csv")