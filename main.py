import streamlit as st
import s3fs
import os
import pandas as pd
import csv


st.title("Welcome to my world")
st.write("### Sucks. Isn't it?")
    
fs = s3fs.S3FileSystem(anon=False)

# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def read_file(filename):
    with fs.open(filename,'r') as f:
        file = csv.reader(f)
        df = pd.DataFrame(file)
        df.columns = df.iloc[0,:].values
        st.write(df)

content = read_file("library-scraping-storage/library_schedule_10_29.csv")

# Print results.

