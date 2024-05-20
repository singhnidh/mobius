import streamlit as st
import pandas as pd
import requests
import re
import altair as alt
import os

st.set_page_config(layout="wide")
st.title("Chat with Data...")

def extract_code_from_text(text):
    pattern = r'```python\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

@st.cache
def get_file_content_as_string(file):
    file.seek(0)
    return file.getvalue()

def get_file_type(uploaded_file):
    if uploaded_file is not None:
        _, file_extension = os.path.splitext(uploaded_file.name)
        if file_extension.lower() == '.csv':
            return 'CSV'
        elif file_extension.lower() == '.txt':
            return 'Text'
    return None

def get_sql_response(df, question, uploaded_file):
    file_type = get_file_type(uploaded_file)
    plot_prompt = {
        "prompt": f"""You are a data analyst at a company. ...priority: always assign the code components for charts under "chart" variable and always sort it by a numeric column based on user query
        Uploaded file is: {file_type}
        """.format(df, question)
    }

    response = requests.post(model_url, json=plot_prompt, headers=headers)
    return response.json()['text']

with st.sidebar:
    st.sidebar.image("logo-black.png")
    uploaded_file = st.file_uploader("Please upload a file")

if uploaded_file is not None:
    file_content = get_file_content_as_string(uploaded_file)
    st.write("File Content:")
    st.code(file_content)

user_query = st.text_input("Type your question.....")
if user_query:
    st.markdown(user_query)
    plot_response = extract_code_from_text(get_sql_response(df=None, question=user_query, uploaded_file=uploaded_file))
    if plot_response:
        try:
            exec(plot_response)
            if 'chart' in globals():
                chart = globals()['chart']
                if isinstance(chart, alt.Chart):
                    st.altair_chart(chart.interactive(), use_container_width=True)
                else:
                    st.error("The generated chart is not valid.")
            else:
                st.error("No chart found in the code output.")
        except Exception as e:
            print(e)
            st.markdown("No Plot for the above query")
