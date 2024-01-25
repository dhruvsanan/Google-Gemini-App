from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import PyPDF2 as pdf
import re
from stqdm import stqdm

import google.generativeai as genai

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt, pdf_content, input):
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content([prompt, pdf_content, input])
        return response.text
    except Exception as e:
        st.error("Internal server error. Please check your internet connection and try again.")
        raise e
def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text


st.set_page_config(page_title="Resume Expert")

st.header("JobFit Analyzer")
st.subheader('This Application helps you in your Resume Review with help of GEMINI AI [LLM]')
jt = st.text_input("Job Title: ", key="jt")
jd = st.text_area("Job Description: ", key="jd")
cutoff = st.number_input("Enter a cutoff percentage (Ideally: 75)", value=None, placeholder="Type a number...", max_value=100, min_value=1)
uploaded_files = st.file_uploader("Upload your Resume(PDF)...", type=["pdf"], accept_multiple_files=True)
pdf_content = ""

if uploaded_files is not None:
    st.write("PDF Uploaded Successfully")

submit = st.button("Percentage match")

input_prompt4 = """
You are an skilled ATS (Applicant Tracking System) scanner with ATS functionality, 
your task is to evaluate the resume against the provided job description. As a Human Resource manager, give me the percentage of match if the resume matches
the job description. Try to give an accurate percentage match based on the keywords in resume and job description. Also, based upon candidate's suitability for the role in job description.
First the output should come as Percentage Match. In addition to this, justify why did you give such Percentage Match.
"""

percentage_matches=[]
if submit:
    if uploaded_files is not None:
        if cutoff:
            if jt:
                input_promptjt="You are expert in the field of "+ jt + ". You have so much experience being HR of that field.  "   """
                    You are an skilled ATS (Applicant Tracking System) scanner with ATS functionality, 
                    your task is to evaluate the resume against the provided job description. As a Human Resource manager, give me the percentage of match if the resume matches
                    the job description. Try to give an accurate percentage match based on the keywords in resume and job description. Also, based upon candidate's suitability for the role in job description.
                    First the output should come as Percentage Match. In addition to this, justify why did you give such Percentage Match.
                    """
                for uploaded_file in stqdm(uploaded_files):
                    pdf_content = input_pdf_text(uploaded_file)
                    response = get_gemini_response(input_promptjt, pdf_content, jd)
                    if response is not None:
                        percentage_match = re.search(r"Percentage Match: (\d+)%", response).group(1)
                        percentage_match_int = int(percentage_match)
                        percentage_matches.append((percentage_match_int, uploaded_file.name))
                    else:
                        st.error("No response received from the server. Please try again.")
            else:
                for uploaded_file in stqdm(uploaded_files):
                    pdf_content = input_pdf_text(uploaded_file)
                    response = get_gemini_response(input_prompt4, pdf_content, jd)
                    st.write(response)
                    percentage_match = re.search(r"Percentage Match: (\d+)%", response).group(1)
                    percentage_match_int = int(percentage_match)
                    if percentage_match_int>= cutoff:
                        percentage_matches.append((percentage_match_int, uploaded_file.name))
        else:
            st.write("Please enter a cutoff percentage")

        percentage_matches.sort(reverse=True)
        for percentage_match, uploaded_file_name in percentage_matches:
            if percentage_match>= cutoff:
                st.subheader("File: " + uploaded_file_name)
                st.success("Percentage Match: " + str(percentage_match) + "%")
            else:
                st.subheader("File: " + uploaded_file_name)
                st.error("Percentage Match: " + str(percentage_match) + "%")
            # st.download_button(
            #     label="Download File",
            #     data=uploaded_file.read(),
            #     file_name=uploaded_file.name,
            #     mime_type="application/pdf"
            # )
            # with open(uploaded_file.name, "rb") as pdf_file:
            #     PDFbyte = uploaded_file.read()

            # st.download_button(label="Download Resume",
            #                     data=PDFbyte,
            #                     file_name=uploaded_file.name,
            #                     mime='application/octet-stream')
    else:
        st.write("Please upload a PDF file to proceed.")


st.markdown("---")
st.caption("Resume Expert - Making Job Applications Easier")