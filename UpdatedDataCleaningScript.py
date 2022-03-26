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

    fouram = stringToDate('2030-01-01 04:00:00.000').time()
    eightam = stringToDate('2030-01-01 08:00:00.000').time()
    twelvepm = stringToDate('2030-01-01 12:00:00.000').time()
    fourpm = stringToDate('2030-01-01 16:00:00.000').time()
    eightpm = stringToDate('2030-01-01 20:00:00.000').time()


    #Creates an indicator variable about what time of day the question was answered - Welcome to change to whatever time brackets
    master['WeeHours'] = master['TimeAnswered'].apply(lambda time: time < fouram)
    master['EarlyMorning'] = master['TimeAnswered'].apply(lambda time: time >= fouram and time < eightam)
    master['MidMorning'] = master['TimeAnswered'].apply(lambda time: time >= eightam and time < twelvepm)
    master['Afternoon'] = master['TimeAnswered'].apply(lambda time: time >= twelvepm and time < fourpm)
    master['Evening'] = master['TimeAnswered'].apply(lambda time: time >= fourpm and time < eightpm)
    master['Night'] = master['TimeAnswered'].apply(lambda time: time >= eightpm)
    
    return master