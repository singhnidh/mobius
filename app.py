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
    "Accept" : "application/json",
    "content-Type" : "application/json"
    }

# {"prompt" : "Give me SQL query for selecting top 10 values of a column, just generate code alone, no extra text, strings or any natural language, not even the suggested steps, not even backticks"}

def get_sql_response(df, question):
        plot_prompt = {
            "prompt":f"""You are a data analyst at a company. You are interacting with a user who wants to create python visualization report based on the data.
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
        # print(response.json()['text'])
        return response.json()['text']

user_query = st.chat_input("Type your question.....")
if user_query is not None:
    st.markdown(user_query)
    plot_response = extract_code_from_text(get_sql_response(df = df, question = user_query))
    print(plot_response)
    # st.write(response)
    try:
            exec(plot_response)
            if 'chart' in globals():
                    # Access the 'chart' object
                    chart = globals()['chart']
                    # Check if 'chart' is an Altair chart object
                    if isinstance(chart, alt.Chart):
                        # Display the Altair chart
                        st.altair_chart(chart.interactive(), use_container_width=True)
                    else:
                        # Handle the case where 'chart' is not an Altair chart object
                        st.error("The generated chart is not valid.")
            else:
                # Handle the case where 'chart' is not defined in the executed code
                 st.error("No chart found in the code output.")
    except Exception as e:
        print(e)
        st.markdown("No Plot for the above query")