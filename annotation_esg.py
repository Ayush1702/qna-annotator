import streamlit as st
import pandas as pd
import numpy as np

st.header("Annotation Tool for Question Answering")
def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(https://unsplash.com/photos/7BjhtdogU3A/download?ixid=MnwxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNjYyMjgwMjYw&force=true);
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
set_bg_hack_url()

if 'count' not in st.session_state:
    st.session_state.count = 0
if 'ctxt' not in st.session_state:
    st.session_state.ctxt = None
if 'desc' not in st.session_state:
    st.session_state.desc = None
title =  "Context Paragraph: {cnt}".format(cnt=st.session_state.count)
with st.form("my_form"):
    with st.sidebar:
        uploaded_file = st.file_uploader("Choose a CSV file")
        ctxt_col = st.text_input("Enter Column Name containing Contexts")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
    if submitted:
        with open("descriptions.csv", "wb") as f:
            f.write(uploaded_file.getvalue())
        desc=pd.read_csv("descriptions.csv")
        st.session_state.desc=desc

if st.session_state.desc is None:
    st.text_area(title, st.session_state.ctxt, height = 250)
else:
    st.text_area(title, st.session_state.desc[ctxt_col][st.session_state.count], height = 250)

New_Labels = ["question", "answer_start", "context", "text"]
save_df = pd.DataFrame(columns=New_Labels)

if 'df' not in st.session_state:
    st.session_state.df = save_df
# question = st.text_input('Enter Question')
question_selectbox = st.selectbox(
    "Select Question",
    ("What is the emission reduction methodology or mechanism used here?","What is the emission reduction target aimed?")
)
answer = st.text_input('Enter Answer')

import re

@st.experimental_singleton
def assign_random_id(df, context_col, id_col):
    """
    Assign random but same id as per context value in a dataframe
    """
    df[id_col] = np.nan
    for context in df[context_col].unique():
        df.loc[df[context_col] == context, id_col] = np.random.randint(1, 1000000)
    return df

@st.experimental_singleton
def find_substring(string, substring):
    """
    Find the start and end position of a substring in a string
    """
    substring = re.escape(substring)
    pattern = re.compile(substring)
    match = pattern.search(string)
    if match:
        return match.start(), match.end()
    else:
        return 0, 0

if st.button("Save"):
    start, end = find_substring(st.session_state.desc[ctxt_col][st.session_state.count], answer)
    st.write("Answer start and end positions: ", start, end)
    save_list = [question_selectbox, start, st.session_state.desc[ctxt_col][st.session_state.count], answer]
    append_df = pd.DataFrame([save_list])
    append_df.columns = New_Labels
    append_df = assign_random_id(append_df, 'context', 'id')
    target_df = pd.concat([st.session_state.df, append_df])
    st.session_state.df = target_df
    st.dataframe(target_df)
st.sidebar.write("No of Documents Annotated: ", len(st.session_state.df))
@st.cache
def convert_df(df):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(st.session_state.df)
st.sidebar.download_button(
     label="Download data as CSV",
     data=csv,
     file_name='squad_format.csv',
 )
col1, col2 = st.columns([1,2])

with col2:
    if st.button("Next"):
        st.session_state.count += 1
        st.experimental_singleton.clear()
with col1:
    if st.button("Previous"):
        if st.session_state.count != 0:
            st.session_state.count -= 1