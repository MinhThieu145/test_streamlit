import streamlit as st
import s3fs
import os
import pandas as pd
import csv
from datetime import datetime

from ExtraClasses import AvailabilityEachDay

st.title("Welcome to my world")
st.write("### Sucks. Isn't it?")
    
fs = s3fs.S3FileSystem(anon=False)

# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def read_file(filename):
    with fs.open(filename,'r') as f:
        file = csv.DictReader(f)
        df = pd.DataFrame(file)

        return df
        st.write(df)

        
# import df
df = read_file("library-scraping-storage/library_schedule_10_29.csv")
st.write(df)



# Get the length of the block we want to find
st.write('### The length of your study session')
study_length = st.select_slider('no value', options=['15 min','30 min','45 min','1 hour',
                                                                '1 hour 15 min', '1 hour 30 min', '1 hour 45 min', '2 hour'],
                                                                 label_visibility='collapsed')

st.write('you study for: ', study_length)



# The week list is still in Indext date type
week_list = pd.date_range(start='10-23-2022', end='12-12-2022', freq='W').strftime("%Y-%m-%d").tolist()

st.write('### Select the week range you want to view')
start_week, end_week = st.select_slider(
    ' blank',
    options= week_list,
    value=(week_list[0], week_list[len(week_list) - 1]) ,
    label_visibility= 'collapsed'
)

week_count = week_list.index(end_week) - week_list.index(start_week)
if week_count > 1:
    st.write('You select: ',week_count , 'weeks')
else:
    st.write('You select: ', week_count, 'week')


st.write(' ### Choose the time range you want to view')
# Select the time 


col1, col2, col3, col4, col5 = st.columns(spec=[1,1,1,1,1])

hour_list = ['06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
minute_list = ['00','15','30','45']

with col1:
    start_hour = st.selectbox(label='hour', options= hour_list)
with col2:
    start_minute = st.selectbox(label='minute', options=minute_list)
with col4:
    hour_list_after = [x for x in hour_list if x >= start_hour]

    end_hour = st.selectbox(label='hour', options= hour_list_after, key='hour_list_1')


with col5:
    def make_minute_list():
        if (start_hour == end_hour):
            return [x for x in minute_list if x > start_minute]
        else:
            return minute_list
    minute_list_after = make_minute_list()

    end_minute = st.selectbox(label='minute', options=minute_list_after,key='minute_list_1')

def ConvertStudyLength(study_length):
    switcher = {
        '15 min':1,
        '30 min':2,
        '45 min':3,
        '1 hour':4,
        '1 hour 15 min' : 5,
        '1 hour 30 min' : 6,
        '1 hour 45 min' : 7,
        '2 hour':8
    }

    return switcher.get(study_length)


def ApplyUserOptions(df):
    # Select the best week
    df = df[(start_week <= df.day_check) & (df.day_check < end_week)]
    
    # Select the hour
    start_hour_min = start_hour +':' + start_minute
    end_hour_min = str(end_hour) + ':'+str(end_minute)
    df = df[ (start_hour_min <= df.hour) & (df.hour <= end_hour_min)]

    return df

def CountHourBlockDay(study_length_convert, each_room_each_day_df):
    i = 0
    n= study_length_convert
    study_block_count = 0

    while i <= len(each_room_each_day_df):
        status_list = each_room_each_day_df.iloc[i:i+n,:].status.tolist()
        
        if ( 
            ('Unavailable' not in status_list) & # condition 1: đéo có cái Unavailable ở đây
            (len(status_list) == n) # Phải đủ 4 block continuos
            ):
            temp_df = each_room_each_day_df.iloc[i:i+4,:]
            result_df = pd.concat([temp_df, result_df])
            i = i + n

            study_block_count += 1
    
        i += 1



    

def CountHourBlock(df):
    # will chỉnh later
    count_each_day_of_week = {}
    result_df = pd.DataFrame(columns=df.columns)
    
    for day_of_week in df.day_of_week.unique().tolist():
        each_day_df = df[df.day_of_week == day_of_week]

        # now calculate it for each room:
        for room in each_day_df.room:
            each_room_each_day_df = each_day_df[each_day_df.room == room]
            CountHourBlockDay()

        break

    return df

def ProprecessDataframe(df):
    # Convert the hour column -> make it to 24-hour instead
    def convert_12_24_time(time):
        in_time = datetime.strptime(time, "%I:%M%p")
        out_time = datetime.strftime(in_time, "%H:%M")
        
        return out_time
    
    df.hour = df.hour.map(lambda x: convert_12_24_time(str(x)))

    # Handle the check_time columns -> there are many problems with it
    df['day_check'] = df.checking_time_utc.map(lambda x: x.split('_')[0])   
    df['time_check'] = df.checking_time_utc.map(lambda x: (x.split('_')[1]))
    # strip the second away and convert to etc time 
    def strip_second(time):
        in_time = datetime.strptime(time,'%H:%M:%S')
        in_time =  pd.to_datetime(in_time) - pd.DateOffset(hours=4)
        out_time = datetime.strftime(in_time, '%H:%M')
        return out_time

    df['time_check'] = df.time_check.map(lambda x: strip_second(x))


    # Rearrange the columns
    df = df[[ 'day_check', 'time_check','hour', 'day_of_week', 'date','room','status']]

    # Now apply the users' filter to the dataframe
    df = ApplyUserOptions(df=df)

    return df


st.write('### Dataframe after proprocessed')
st.write(ProprecessDataframe(df=df))

saturday_availability = AvailabilityEachDay(day_of_week='Saturday')
st.write(saturday_availability.day_of_week)




