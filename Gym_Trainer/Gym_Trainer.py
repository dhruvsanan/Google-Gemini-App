from dotenv import load_dotenv

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image


genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model = genai.GenerativeModel("gemini-1.5-pro")


def gemini_response(input, image, prompt, input_prompt2):
    if input:
        if image:
            response = image_model.generate_content(
                [input, image, prompt+input_prompt2], stream=True, safety_settings={'HARASSMENT': 'block_none', })
        else:
            response = image_model.generate_content(
                [input, prompt], stream=True, safety_settings={'HARASSMENT': 'block_none'})
    else:
        response = image_model.generate_content(
            [image, prompt+input_prompt2], stream=True, safety_settings={'HARASSMENT': 'block_none'})
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
                You are an expert gymming trainer. Consider yourself as a profesional trainer who provides training plans.
                """
    input_prompt2 = """
                You will receive an image of a body &
                you give a rough estimate of what the body type might be and
                    answer questions based on the input image and
                    in addition to that provide a complementry gym routine for a week tailored to the input image.
                Make sure you act as a professional trainner. Don't try to give no as answer. Even if you don't understand, just give a generic answer.
                """

    submit = st.button("Tell me about my body")

    if submit:
        response = gemini_response(input, image, input_prompt, input_prompt2)
        st.subheader("The Response is")
        for chunk in response:
            st.write(chunk.text)


if __name__ == '__main__':
    main()
