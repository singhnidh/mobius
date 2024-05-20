import streamlit as st
import pandas as pd
import requests
import re
import altair as alt

st.set_page_config(layout="wide")
st.title("Chat with Data...")


def extract_code_from_text(text):
    # Regular expression pattern to match code between triple single quotes
    pattern = r'```python\n(.*?)```'
    # Use re.search to find the first match of the pattern in the text
    match = re.search(pattern, text, re.DOTALL)
    # If a match is found, return the code inside triple quotes, otherwise return None
    if match:
        return match.group(1)
    else:
        return None


with st.sidebar:
    st.sidebar.image("logo-black.png")
    # st.sidebar.subheader("Upload your file")
    uploaded_file = st.file_uploader("Please upload a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # st.dataframe(df)
else:
    st.write("Please upload a file into the application")

# --------------------------------------------------------

model_url = "http://10.101.11.23:8000/deepseek_ai_model"
headers = {
    "Accept": "application/json",
    "content-Type": "application/json"
}


def get_plot_description(df, question):
    plot_prompt = {
        "prompt": f"""You are a data analyst at a company. You are interacting with a user who wants to create python visualization report based on the data.
        Based on the below dataframe called as df and user query write a python query to plot the output data in a python graph. The below dataframe contains the required information, you need to answer the question.

        ddf : {df}
        df = pd.read_csv(uploaded_file)
        question : {question}
        
        For example:
        Question: Presenting categorical data using a bar chart to compare different categories or groups
        Python Query: 
                    categories = ['A', 'B', 'C', 'D']
                    values = [20, 30, 25, 35]

                    # Create a bar chart
                    fig = go.Figure(data=[go.Bar(x=categories, y=values)])
                    fig.update_layout(title='Bar Chart', xaxis_title='Categories', yaxis_title='Values')
                    fig.show()
        Always sort it with 'X' or 'Y' prefixes/alias
        Question: Create a bar chart using Altair        # 
        python query: 
            chart = alt.Chart(df).mark_bar().encode(
            x=('Language', sort = '-y'),
            y='TotalPopulation',
            color='Language'
    )

        Write the python query to create plots and graphs from the dataframe and nothing else. 
        Do not wrap the python query in any other text, not even backticks.
        Use only "altair" library to plot the graphs and "Pandas" for connection and dataframe handling using required orderby & groupby clauses.

        priority: always assign the code compoents for charts under "chart" variable and always sort it by a numeric column based on user query
        
        You can return none if the data frame has just only 1 column or only 1 row or if the plot is more complicated to fit in traditional plotting style.
        Your turn:
        """.format(df, question)
    }

    response = requests.post(model_url, json=plot_prompt, headers=headers)
    return response.json()['text']


user_query = st.chat_input("Type your question.....")
if user_query is not None:
    st.markdown(user_query)
    plot_response = extract_code_from_text(get_plot_description(df=df, question=user_query))

    try:
        if plot_response:
            st.write("Generated Plot Description:")
            st.code(plot_response, language='text')
        else:
            st.error("No plot description found for the given query.")
    except Exception as e:
        st.error("An error occurred while processing the plot description.")
        st.write(e)
