import google.generativeai as genai
from stqdm import stqdm
import re
import PyPDF2 as pdf
import os
import streamlit as st
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_job_description(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    job_description_section = soup.find("section", {"class": "description"})
    job_description = job_description_section.get_text(strip=True)
    return job_description


def get_gemini_response(prompt, pdf_content, input):
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content([prompt, pdf_content, input])
        return response.text
    except Exception as e:
        st.error(
            "Internal server error. Please check your internet connection and try again.")
        raise e


def input_pdf_text(uploaded_file):
    if uploaded_file is not None:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text
    else:
        st.write("Please upload a PDF file to proceed.")


def process_uploaded_files(uploaded_files, input_promptjt, jd, cutoff):
    percentage_matches = []
    for uploaded_file in stqdm(uploaded_files):
        pdf_content = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_promptjt, pdf_content, jd)
        if response is not None:
            match = re.search(r"Percentage Match: (\d+)%", response)
            if match:
                percentage_match = match.group(1)
            else:
                match = re.search(r"(\d+)%", response)
                percentage_match = match.group(1)
            percentage_match_int = int(percentage_match)
            percentage_matches.append(
                (percentage_match_int, uploaded_file.name, uploaded_file))
        else:
            st.error(
                "No response received from the server. Please try again."
            )

    percentage_matches.sort(reverse=True)
    return percentage_matches


st.set_page_config(page_title="Resume Expert")

st.header("Smart ATS")
st.subheader(
    'This Application helps you shortlist resumes with help of GEMINI AI [LLM]')
jdButton = st.radio(
    "Jd format",
    ["LinkedIn URL", "Text JD"], )
job_url = ""
pdf_content = ""
jt = ""
jd = ""
if jdButton == "LinkedIn URL":
    job_url = st.text_input("LinkedIn Job URL")
    if job_url:
        try:
            jd = extract_job_description(job_url)
            st.write("URL processed successfully.")
        except Exception:
            st.write("There is an error. Please write a job description manually.")
else:
    jt = st.text_input("Job Title: ", key="jt")
    jd = st.text_area("Job Description: ", key="jd")
cutoff = st.number_input("Enter a cutoff percentage (Ideally: 75)",
                         value=75, placeholder="Type a number...", max_value=100, min_value=1)
uploaded_files = st.file_uploader("Upload your Resumes(PDF)...", type=[
                                  "pdf"], accept_multiple_files=True)

submit = st.button("Percentage match")
clear_button = st.button("Clear Results")
if clear_button:
    st.session_state['percentage_matches'] = []
input_promptjt = "You are expert in the field of " + jt + ". You have so much experience being HR of that field.  "   """
                You are an skilled ATS (Applicant Tracking System) scanner with ATS functionality, 
                your task is to evaluate the resume against the provided job description. As a Human Resource manager, give me the percentage of match if the resume matches
                the job description. Try to give an accurate percentage match based on the keywords in resume and job description. Also, based upon candidate's suitability for the role in job description.
                First the output should come as Percentage Match. In addition to this, justify why did you give such Percentage Match.
                """
if 'percentage_matches' not in st.session_state:
    st.session_state['percentage_matches'] = []

if submit:
    if jd:
        if uploaded_files:
            percentage_matches = process_uploaded_files(
                uploaded_files, input_promptjt, jd, cutoff)
            st.session_state['percentage_matches'] = percentage_matches
        else:
            st.error(
                "Please Upload a file")
    else:
        st.write("Please write a job description")

if st.session_state['percentage_matches']:
    for i, (percentage_match, uploaded_file_name, uploaded_file) in enumerate(st.session_state['percentage_matches']):
        if percentage_match >= cutoff:
            st.subheader("File: " + uploaded_file_name)
            st.success("Percentage Match: " + str(percentage_match) + "%")
        else:
            st.subheader("File: " + uploaded_file_name)
            st.error("Percentage Match: " + str(percentage_match) + "%")
        st.download_button(
            label="Download File",
            data=uploaded_file,
            file_name=uploaded_file_name,
            key=f"{uploaded_file.name}_{i}",  # Combine filename and index
        )


st.markdown("---")
st.caption("Resume Expert - Making Resume Shortlisting Easier")
