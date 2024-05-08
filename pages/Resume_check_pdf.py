import requests
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

load_dotenv()  # load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')


def extract_job_description(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    job_description_section = soup.find("section", {"class": "description"})
    job_description = job_description_section.get_text()
    job_description = job_description.strip()
    return job_description


def get_gemini_repsonse(input_prompt4, text, jd):
    if jd:
        response = model.generate_content([input_prompt4, text, jd])
        return response.text
    else:
        st.write("Please write a Jd")


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


# Prompt Template
input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are an Technical Human Resource Manager with expertise in data science, 
your role is to scrutinize the resume in light of the job description provided. 
Share your insights on the candidate's suitability for the role from an HR perspective. 
Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. As a Human Resource manager,
 assess the compatibility of the resume with the role. Give me what are the keywords that are missing
 Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
"""
input_prompt4 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""
input_prompt5 = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Answer the following question based on the resume of the candidate.
"""

# streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
uploaded_file = st.file_uploader(
    "Upload Your Resume", type="pdf", help="Please uplaod the pdf")
jdButton = st.radio(
    "Jd format",
    ["LinkedIn URL", "Text JD"])

if jdButton == "LinkedIn URL":
    job_url = st.text_input("LinkedIn Job URL")
else:
    jd = st.text_area("Paste the Job Description")


submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("What are the Keywords That are Missing")

submit4 = st.button("Percentage match")
question = st.text_input("What do you want to know?")
submit = st.button("Info from resume")
submit1 = st.button("Tell Me About the Resume")


if submit:
    text = input_pdf_text(uploaded_file)
    if question:
        response = get_gemini_repsonse(input_prompt5, text, question)
        st.subheader(response)
    else:
        st.write("Please ask a question")

elif submit1:
    text = input_pdf_text(uploaded_file)
    response = model.generate_content([input_prompt1, text])
    st.subheader(response.text)

elif submit2:
    if job_url:
        text = input_pdf_text(uploaded_file)
        jd = extract_job_description(job_url)
        parts = jd.rsplit("Powered by ", 1)
        job_description = parts[0]
        response = get_gemini_repsonse(input_prompt2, text, jd)
        st.subheader(response)
    else:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_repsonse(input_prompt2, text, jd)
        st.subheader(response)

elif submit3:
    if job_url:
        text = input_pdf_text(uploaded_file)
        jd = extract_job_description(job_url)
        parts = jd.rsplit("Powered by ", 1)
        job_description = parts[0]
        response = get_gemini_repsonse(input_prompt3, text, jd)
        st.subheader(response)
    else:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_repsonse(input_prompt3, text, jd)
        st.subheader(response)

elif submit4:
    if job_url:
        text = input_pdf_text(uploaded_file)
        jd = extract_job_description(job_url)
        parts = jd.rsplit("Powered by ", 1)
        job_description = parts[0]
        response = get_gemini_repsonse(input_prompt4, text, jd)
        st.subheader(response)
    else:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_repsonse(input_prompt4, text, jd)
        st.subheader(response)

st.markdown("---")
st.caption("Resume Expert - Making Job Applications Easier")
