import streamlit as st
import pandas as pd
import numpy as np
import sklearn
import seaborn as sns
import matplotlib.pyplot as plt

import chart_studio.plotly as py
import plotly.express as px


st.title("Welcome to my world")
st.write("### Sucks. Isn't it?")
    
# import df
df = pd.read_csv('library_schedule_10_29.csv')

st.write(df)
x_axis_value = st.selectbox('Select Value', options=df.columns)

graph = px.histogram(data_frame=df, x =x_axis_value, text_auto=True)
st.plotly_chart(graph)

x_axis_value = st.selectbox('Select X Value', options=df.columns)

graph = px.histogram(data_frame=df, x =x_axis_value, text_auto=True)
st.plotly_chart(graph)
