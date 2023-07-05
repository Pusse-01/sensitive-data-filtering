import streamlit as st
import os
from utils import scan_text_spacy
from streamlit_option_menu import option_menu
import openai




os.environ['OPENAI_API_KEY'] = st.secrets["key"]
openai.api_key = os.getenv("OPENAI_API_KEY")

def scan_text_page():
    st.title("Scan Text")
    text = st.text_input("Enter your text:")
    submit = st.button("Submit")
    
    if submit and text:
        # if not openai_api_key:
        #     st.info("Please add your OpenAI API key to continue.")
        #     st.stop()
        # os.environ['OPENAI_API_KEY'] = openai_api_key

        findings = scan_text_spacy(text)
        # st.write("Filtered Text:")
        # st.write(findings)
        # st.subheader("After content filtering - this is what will be sent to ChatGPT:\n\n")
        # st.write( findings.text, "\n\n----\n\n")

        # Send prompt to OpenAI model for AI-generated response
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": findings.text}
        ]
        )
        completion2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ]
        )
        # st.subheader("Here's a generated response with Normal Text:\n")
        res_with_normal_text = completion2['choices'][0].message.content
        # st.write(res_with_normal_text )
        # st.subheader("Here's a generated response with Recacted Text:\n")
        res_with_redacted_text = completion['choices'][0].message.content
        data = {
            "Input Text": [text],
            "Redacted Text": [findings.text],
            "OpenAI Response (Normal Text)": [res_with_normal_text],
            "OpenAI Response (Redacted Text)": [res_with_redacted_text]
        } 
        # Display the table
        st.subheader("Generated Responses:")
        st.table(data)
        # st.write(res_with_redacted_text)
        # for finding in findings[0]:
        #     # print(finding[0].finding)
        #     # st.info(f"Finding text: {finding.finding},  Detector name: {finding.detector_name}", icon="ℹ️")
        #     # st.write(f"Finding text: {finding.finding}")
        #     # st.write(f"Detector name: {finding.detector_name}")

        #     st.write("")
    # Add your code for the "Scan Text" page here

def scan_files_page():
    st.write("Scan Files Page")

# 1. as sidebar menu
with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    selected = option_menu("Menu", ["Scan Text", 'Scan Files'], 
        icons=['file-text', 'folder'], menu_icon="cast", default_index=1)
# selected
if selected == "Scan Text":
    scan_text_page()
elif selected == "Scan Files":
    scan_files_page()