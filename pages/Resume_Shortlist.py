from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from PIL import Image
import io
import pdf2image
import base64
import re
from stqdm import stqdm

import google.generativeai as genai

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def handle_image_uploads(uploaded_file):
    # Initialize a list to store the images
    images = []

    # Iterate over the uploaded files
    for idx, file in enumerate(uploaded_file):
        # Create a unique variable name for the image
        image_variable_name = f"image{idx+1}"

        # Open the image using OpenCV
        image = Image.open(file)

        # Assign the image to the unique variable
        globals()[image_variable_name] = image

        # Add the image to the list
        images.append(image)

    # Return the list of images
    return images

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        # Take the first page for simplicity, or loop through images for all pages
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="Resume Expert")

st.header("JobFit Analyzer")
st.subheader('This Application helps you in your Resume Review with help of GEMINI AI [LLM]')
input_text = st.text_area("Job Description: ", key="input")
cutoff = st.number_input("Enter a cutoff percentage", value=None, placeholder="Type a number...", max_value=100, min_value=1)
uploaded_files = st.file_uploader("Upload your Resume(PDF)...", type=["pdf"], accept_multiple_files=True)
pdf_content = ""

if uploaded_files is not None:
    st.write("PDF Uploaded Successfully")

# submit1 = st.button("Tell Me About the Resume")

# submit2 = st.button("How Can I Improvise my Skills")

# submit3 = st.button("What are the Keywords That are Missing")

submit4 = st.button("Percentage match")

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
your task is to evaluate the resume against the provided job description. As a Human Resource manager, give me the percentage of match if the resume matches
the job description. Try to give an accurate percentage match based on the keywords in resume and job description. Also, based upon candidate's suitability for the role in job description.
First the output should come as Percentage Match. In addition to this, justify why did you give such Percentage Match.
"""

# if submit1:
#     if uploaded_file is not None:
#         pdf_content = input_pdf_setup(uploaded_file)
#         response = get_gemini_response(input_prompt1, pdf_content, input_text)
#         st.subheader("The Response is")
#         st.write(response)
#     else:
#         st.write("Please upload a PDF file to proceed.")

# elif submit2:
#     if uploaded_file is not None:
#         pdf_content = input_pdf_setup(uploaded_file)
#         response = get_gemini_response(input_prompt2, pdf_content, input_text)
#         st.subheader("The Response is")
#         st.write(response)
#     else:
#         st.write("Please upload a PDF file to proceed.")

# elif submit3:
#     if uploaded_file is not None:
#         pdf_content = input_pdf_setup(uploaded_file)
#         response = get_gemini_response(input_prompt3, pdf_content, input_text)
#         st.subheader("The Response is")
#         st.write(response)
#     else:
#         st.write("Please upload a PDF file to proceed.")
percentage_matches=[]
if submit4:
    if uploaded_files is not None:
        if cutoff:
            for uploaded_file in stqdm(uploaded_files):
            # for uploaded_file in uploaded_files:

                pdf_content = input_pdf_setup(uploaded_file)
                response = get_gemini_response(input_prompt4, pdf_content, input_text)
                # st.write(response)
                percentage_match = re.search(r"Percentage Match: (\d+)%", response).group(1)
                # Convert the percentage match to an integer
                percentage_match_int = int(percentage_match)
                if percentage_match_int>= cutoff:
                    percentage_matches.append((percentage_match_int, uploaded_file.name))
        else:
            st.write("Please enter a cutoff percentage")

            # Check if the percentage match is greater than 70%
        percentage_matches.sort(reverse=True)
        for percentage_match, uploaded_file_name in percentage_matches:
            st.subheader("File: " + uploaded_file_name)
            st.write("Percentage Match: " + str(percentage_match) + "%")
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