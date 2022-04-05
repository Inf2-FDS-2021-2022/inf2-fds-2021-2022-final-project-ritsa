import pandas as pd
import numpy as np
import re
from datetime import datetime

def clean_array(substrs):
    # cleans split string substrings into an array of ints
    cleaned_substr = []
    for substr in substrs:
        substr = re.sub(' ', '', substr)
        substr = re.sub('\[', '', substr)
        substr = re.sub('\]', '', substr)
        substr = re.sub(',', '', substr)
        if len(substr) == 0:
            cleaned_substr.append(1000)
        else:
            cleaned_substr.append(int(substr))
    return cleaned_substr

def isOverConfident(IsCorrect, Confidence):
    if IsCorrect == 0 and Confidence >= 75:
        return 1
    else:
        return 0
    
def isUnderConfident(IsCorrect, Confidence):
    if IsCorrect == 1 and Confidence <= 25:
        return 1
    else:
        return 0

def stringToDate(string):
    # Tom's function :) - cleans string to a date
    if type(string) != str:
        return stringToDate('2030-01-01 00:00:00.000') # indicator variable for no given DOB
    else:
        date = datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f")
        return date

def cleanData():

    # reads in all the datasets we will be using
    maindata = pd.read_csv('https://www.inf.ed.ac.uk/teaching/courses/fds/data/project-2021-2022/eedi/task_3_4.csv.gz')
    subdata = pd.read_csv('https://www.inf.ed.ac.uk/teaching/courses/fds/data/project-2021-2022/eedi/subject_metadata.csv.gz')
    questiondata = pd.read_csv('https://www.inf.ed.ac.uk/teaching/courses/fds/data/project-2021-2022/eedi/question_metadata_task_3_4.csv.gz')
    studentdata = pd.read_csv('https://www.inf.ed.ac.uk/teaching/courses/fds/data/project-2021-2022/eedi/student_metadata_task_3_4.csv.gz')
    answerdata = pd.read_csv('https://www.inf.ed.ac.uk/teaching/courses/fds/data/project-2021-2022/eedi/answer_metadata_task_3_4.csv.gz')

    merged_answer_data = pd.merge(maindata, answerdata, on = "AnswerId")
    # renamed to master here just out of laziness
    master = pd.merge(merged_answer_data, studentdata, on = "UserId")

    # uses Tom's date cleaning function to clean columns with dates
    master['DateOfBirth'] = master['DateOfBirth'].apply(lambda date: stringToDate(date))
    master['DateAnswered'] = master['DateAnswered'].apply(lambda date: stringToDate(date))

    # this creates an indicator for if a question hasn't been answered
    master['IsAnswered'] = master['AnswerValue'].apply(lambda x : not np.isnan(x))

    # extracts the time answered from the date answered for easier analysis
    master['TimeAnswered'] = master['DateAnswered'].apply(lambda x: x.time())

    
    master['HourAnswered'] = master['TimeAnswered'].apply(lambda x: x.hour)
    
    master['Age'] = master.apply(lambda row : (row['DateAnswered']- row['DateOfBirth']).days // 365.25, axis = 1)
    
    # only loosing 116 records from 1.3 million
    master = master[master['Age'] < 20]


    #Creates an indicator variable about what time of day the question was answered - Welcome to change to whatever time brackets
    master['TimeSlot'] = master['HourAnswered'].apply(lambda time: 'WeeHours' if time < 4 else ('EarlyMorning' if time < 8 else ('MidMorning' if time < 12 else('Afternoon' if time < 16 else('Evening' if time < 20 else 'Night')))))
    
    master['WeeHours'] = master['HourAnswered'].apply(lambda time: time < 4)
    master['EarlyMorning'] = master['HourAnswered'].apply(lambda time: time >= 4 and time < 8)
    master['MidMorning'] = master['HourAnswered'].apply(lambda time: time >= 8 and time < 12)
    master['Afternoon'] = master['HourAnswered'].apply(lambda time: time >= 12 and time < 16)
    master['Evening'] = master['HourAnswered'].apply(lambda time: time >= 16 and time < 20)
    master['Night'] = master['HourAnswered'].apply(lambda time: time >= 20)
 
    master['Overconfidence'] = master.apply(lambda row: isOverConfident(row['IsCorrect'], row['Confidence']), axis = 1)
    master['Underconfidence'] = master.apply(lambda row: isUnderConfident(row['IsCorrect'], row['Confidence']), axis = 1)
    
    return master
