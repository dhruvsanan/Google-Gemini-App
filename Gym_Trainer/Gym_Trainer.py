from dotenv import load_dotenv

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image


genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model = genai.GenerativeModel("gemini-1.5-pro")
text_model = genai.GenerativeModel("gemini-pro")


def gemini_response(input, image, prompt):
    if input:
        if image:
            response = image_model.generate_content(
                [input, image, prompt], stream=True, safety_settings={'HARASSMENT': 'block_none', })
        else:
            response = image_model.generate_content(
                [input, prompt], stream=True, safety_settings={'HARASSMENT': 'block_none'})

    else:
        response = image_model.generate_content(
            [image, prompt], stream=True, safety_settings={'HARASSMENT': 'block_none'})
    return response


def main():
    load_dotenv()
    st.set_page_config(page_title="Gemini Gym Trainer")

    st.header("Gemini Image")

    input = st.text_input("Ask a question ", key="input")
    uploaded_file = st.file_uploader("Upload the image of your body", type=[
                                     "jpg", "jpeg", "png", "webp"])
    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    input_prompt = """
                You are an expert gymming trainer.
                You will receive an input image of a body &
                you will have to analyse the body type and 
                state the body type of the person and
                    answer questions based on the input image and
                    in addition to that provide a complementry gym routine for a week tailored to the input image.
                """

    submit = st.button("Tell me about my body")

    if submit:
        response = gemini_response(input, image, input_prompt)
        st.subheader("The Response is")
        for chunk in response:
            st.write(chunk.text)


if __name__ == '__main__':
    main()
