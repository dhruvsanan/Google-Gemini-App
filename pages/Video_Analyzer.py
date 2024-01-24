from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import tempfile
import google.generativeai as genai
from PIL import Image
import base64
import io
import numpy as np
import cv2
genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model=genai.GenerativeModel("gemini-pro-vision")
import datetime
import openai
import sys

from audio_recorder_streamlit import audio_recorder

openai.api_key = os.getenv("OPENAI_API_KEY")

def save_uploaded_video(video_file, file_path):
    with open(file_path, "wb") as f:
        f.write(video_file.read())
def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = 0
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = frame_rate
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        frame_count += 1
    cap.release()
    return frames
def handle_image_uploads(uploaded_file):
    images = []
    for idx, file in enumerate(uploaded_file):
        image_variable_name = f"image{idx+1}"
        image = Image.fromarray(file)
        globals()[image_variable_name] = image
        images.append(image)
    return images
def create_image(data):
    image_bytes = base64.b64decode(data)
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    return image
def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript
def save_audio_file(audio_bytes, file_extension):
    """
    Save audio bytes to a file with the specified extension.

    :param audio_bytes: Audio data in bytes
    :param file_extension: The extension of the output audio file
    :return: The name of the saved audio file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"

    with open(file_name, "wb") as f:
        f.write(audio_bytes)

    return file_name
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = transcribe(audio_file)
    return transcript["text"]

st.set_page_config(page_title="Video Analyser")

st.header(" Video Analyser")

input = st.text_input("Input: ",key="input")
video_file = st.file_uploader("Upload a video", type=["mp4"])
if video_file:
    file_extension = ".mp3"
    save_audio_file(video_file.read(), file_extension)


submit=st.button("Tell me about the Video")

input_prompt="""
imagine the continuation of the images as a video.
Hey Act Like a skilled or very experience Video Analyzer.
Train your self with only the transcript and the video.
your task is to answer the question only based on the transcript and the video that you recieved.

transcript:{transcript_text}
question:{input}

Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. 
However, you are talking to a non-technical audience, so be sure to break down complicated concepts and 
strike a friendly and converstional tone. 
If the question is out of the transcript or the video, you may ignore it.
"""


if submit: 
    if video_file is not None:
        file_name = video_file.name
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        save_uploaded_video(video_file, file_path)
        frames=get_frames(file_path) 
        images = handle_image_uploads(frames)
        transcript_text = transcribe_audio(file_path)
        st.write(input_prompt)

        response = image_model.generate_content([input_prompt, *images])
        st.subheader("The Response is")
        st.write(response.text)

    else:
        st.write("Please upload a video")
