from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image


genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model=genai.GenerativeModel("gemini-pro-vision")
text_model=genai.GenerativeModel("gemini-pro")


def gemini_response(input,image):
    if input !="":
        if image:
            response = image_model.generate_content([input,image],stream=True)
        else:
            response = text_model.generate_content(input,stream=True)
    else:
        response = image_model.generate_content(image,stream=True)
    return response


# import sys
# import io
# import ffmpeg
# import json

# def main(filename):
#     # Read the video file
#     video = ffmpeg.input(filename)

#     # Extract audio and video streams from the input video
#     audio_stream = video.audio
#     video_stream = video.video

#     # Downscale the video stream to half its original size
#     scaled_video_stream = video_stream.filter('scale', w=-1, h='1080')

#     # Re-encode the audio and video streams using H.264 and AAC codecs
#     output_video = scaled_video_stream.output('output.mp4', vcodec='libx264', acodec='aac', strict='experimental').run()

#     # Generate a JSON metadata file for the output video
#     metadata = {
#         'width': output_video.video.width,
#         'height': output_video.video.height
#     }
#     with io.open('metadata.json', 'w') as f:
#         json.dump(metadata, f)


st.set_page_config(page_title="Gemini Image")

st.header("Gemini Image")

input = st.text_input("Input: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png","webp"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)


submit=st.button("Tell me about the image")


if submit: 
    response=gemini_response(input,image)
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)