import os
import openai
import streamlit as st
from streamlit_option_menu import option_menu
from utils import scan_text_spacy




os.environ['OPENAI_API_KEY'] = st.secrets["key"]

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Sensitive Data Filter to ChatGPT")
text = st.text_area("Enter your text:")
submit = st.button("Submit")

if submit and text:
    findings = scan_text_spacy(text)
    
    st.subheader("Input to ChatGPT:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Text")
        st.write(text)
    with col2:
        st.write("Redacted")
        st.write(findings.text)

    with st.spinner(text="ChatGPT is at work..."):

        # Send prompt to OpenAI model for AI-generated response
        completion = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": findings.text}]
        )
        res_with_redacted_text = completion['choices'][0].message.content

        completion2 = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": text}]
        )
        res_with_normal_text = completion2['choices'][0].message.content

    st.subheader("Generated Responses:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Text")
        st.write(res_with_normal_text)
    with col2:
        st.write("Redacted")
        st.write(res_with_redacted_text)
