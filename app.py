import streamlit as st
import pandas as pd
import io
import os
from dotenv import load_dotenv

from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="Excel AI Chatbot", layout="centered")
st.title("📊 Portfolio Actuals Chatbot with GPT")
st.markdown("Ask questions like: `What is the YTD cost of John?`")

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Initialize variables
df = None
response = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove extra spaces
    st.subheader("📂 Excel Preview")
    st.dataframe(df.head())

# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# User query
user_query = st.text_input("🔍 Ask a question about your data")

# Run only if all inputs are provided
if df is not None and openai_api_key and user_query:
    try:
        llm = OpenAI(api_token=openai_api_key)
        sdf = SmartDataframe(df, config={"llm": llm})
        response = sdf.chat(user_query)
        st.subheader("🤖 GPT Response:")
        st.write(response)

        # If the response is a DataFrame, provide download option
        if isinstance(response, pd.DataFrame):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                response.to_excel(writer, index=False, sheet_name="FilteredData")
            st.download_button(
                label="Download Excel File",
                data=output.getvalue(),
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    if not openai_api_key:
        st.warning("⚠️ OpenAI API key not found in environment variables.")
