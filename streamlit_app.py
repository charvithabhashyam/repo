#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Try importing google.generativeai; if missing, show a friendly error
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("Module 'google-generativeai' not found. Please install it with 'pip install google-generativeai'.")
    st.stop()

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("Google API key not found in environment variables. Please set 'GOOGLE_API_KEY' in your .env file.")
    st.stop()

# Configure the API key for the Generative AI model
genai.configure(api_key=API_KEY)

# Function to get AI response based on the resume and job description
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Prompt template for Generative AI model
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analytics,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive, and you should provide
the best assistance for improving the resumes. Assign the percentage matching based
on JD and the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit app UI
st.title("Application Tracking System (ATS)")
st.text("Improve Your Resume Through ATS")

# Option to paste or upload multiple Job Descriptions
st.header("Job Descriptions")
jd_input_option = st.radio("How would you like to provide job descriptions?", ("Paste JDs", "Upload JD File"))
jds = []

if jd_input_option == "Paste JDs":
    jd_count = st.number_input("How many job descriptions?", min_value=1, step=1, value=1)
    for i in range(jd_count):
        jd_text = st.text_area(f"Paste Job Description {i + 1}")
        if jd_text:
            jds.append(jd_text)

elif jd_input_option == "Upload JD File":
    jd_file = st.file_uploader("Upload a text file containing Job Descriptions (one per line)", type=["txt"])
    if jd_file:
        jds = jd_file.read().decode("utf-8").splitlines()

# Upload multiple resumes
st.header("Resumes")
uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True, help="Please upload PDFs")

submit = st.button("Submit")

if submit:
    if uploaded_files and jds:
        for uploaded_file in uploaded_files:
            st.write(f"Processing resume: {uploaded_file.name}")

            # Extract resume text from PDF
            resume_text = input_pdf_text(uploaded_file)

            # Iterate through all job descriptions for the current resume
            for idx, jd in enumerate(jds):
                st.subheader(f"Results for {uploaded_file.name} (JD {idx + 1})")

                # Format the prompt for the AI model
                prompt = input_prompt.format(text=resume_text, jd=jd)
                response = get_gemini_response(prompt)

                # Parse the AI response
                try:
                    response_json = json.loads(response)
                except json.JSONDecodeError:
                    st.error("There was an error in processing the response. Please try again.")
                    continue

                jd_match = response_json.get("JD Match", "N/A")
                missing_keywords = response_json.get("MissingKeywords", [])
                profile_summary = response_json.get("Profile Summary", "")

                # Dynamic Tabs for viewing results
                tab1, tab2, tab3 = st.tabs(["JD Match", "Missing Keywords", "Profile Summary"])

                with tab1:
                    st.markdown(f"<h3 style='color:green;'>JD Match: {jd_match}</h3>", unsafe_allow_html=True)

                with tab2:
                    if missing_keywords:
                        st.markdown("<h3 style='color:red;'>Missing Keywords</h3>", unsafe_allow_html=True)
                        st.write(", ".join(missing_keywords))
                    else:
                        st.markdown("<h3 style='color:green;'>No Missing Keywords!</h3>", unsafe_allow_html=True)

                with tab3:
                    st.markdown("<h3 style='color:blue;'>Profile Summary</h3>", unsafe_allow_html=True)
                    st.write(profile_summary)

    else:
        st.error("Please upload both resumes and job descriptions to proceed.")




