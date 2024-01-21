from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image


genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model=genai.GenerativeModel("gemini-pro-vision")


def gemini_response(input,image,image2):
    if input !="":
        response = image_model.generate_content([input,image,image2])
    else:
        response = image_model.generate_content(image)
    return response

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


st.set_page_config(page_title="Gemini Image")

st.header("Gemini Image")

input = st.text_input("Input: ",key="input")
uploaded_files = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png","webp"], accept_multiple_files=True, key="image_uploader_1")

images = handle_image_uploads(uploaded_files)

submit=st.button("Tell me about the image")


if submit: 
    response = image_model.generate_content([input, *images])
    st.subheader("The Response is")
    st.write(response.text)