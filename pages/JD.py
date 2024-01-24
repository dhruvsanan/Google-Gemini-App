import streamlit as st 
import requests 
from bs4 import BeautifulSoup

def extract_job_description(url):
    response = requests.get(url) 
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    job_description_section = soup.find("section", {"class": "description"})
    job_description = job_description_section.get_text()
    job_description = job_description.strip()
    return job_description

st.title("LinkedIn Job Description Extractor")

with st.form("job_url_form"):
    job_url = st.text_input("LinkedIn Job URL") 
    submitted = st.form_submit_button("Extract Job Description")

if submitted:
    job_description = extract_job_description(job_url)
    parts = job_description.rsplit("Powered by ", 1)
    job_description = parts[0]
    st.write("Job Description:") 
    st.write(job_description)

