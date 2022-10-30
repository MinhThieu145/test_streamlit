import streamlit as st
import s3fs
import os
import csv


st.title("Welcome to my world")
st.write("### Sucks. Isn't it?")
    
fs = s3fs.S3FileSystem(anon=False)

# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def read_file(filename):
    with fs.open(filename) as f:
        return f.read().decode("utf-8")

content = read_file("library-scraping-storage/library_schedule_10_29.csv")

# Print results.
df = pd.read_csv(content)
st.write(df)
