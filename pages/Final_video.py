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
import math
import datetime
import openai
import sys
genai.configure(api_key=os.getenv("GOOGLE_API _KEY"))

image_model=genai.GenerativeModel("gemini-pro-vision")

def save_uploaded_video(video_file, file_path):
    with open(file_path, "wb") as f:
        f.write(video_file.read())

def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = 0
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    new_frame_interval = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 15)
    frame_interval = frame_rate
    if new_frame_interval > frame_interval:
        frame_interval = new_frame_interval
    frames = []
    st.write(new_frame_interval)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Check if the payload size of the frame exceeds the limit
            payload_size = len(frame.tobytes())
            st.image(frame)
            if payload_size > 4194304:
                # The payload size exceeds the limit, so we cannot send this frame
                continue
            frames.append(frame)
            # st.image(frame)
        frame_count += 1
    cap.release()
    st.write(len(frames))
    return frames
def handle_image_uploads(uploaded_file):
    # Initialize a list to store the images
    images = []

    # Iterate over the uploaded files
    for idx, file in enumerate(uploaded_file):
        # Create a unique variable name for the image
        image_variable_name = f"image{idx+1}"

        # Open the image using OpenCV
        image = Image.fromarray(file)

        # Assign the image to the unique variable
        globals()[image_variable_name] = image

        # Add the image to the list
        images.append(image)

    # Return the list of images
    return images
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

st.set_page_config(page_title="Video Check")

st.header(" Video Check")

input = st.text_input("Input: ",key="input")
video_file = st.file_uploader("Upload a video", type=["mp4"])

# st.write(video_file._file_urls.upload_url)

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
        st.write(transcript_text)
        response = image_model.generate_content([input_prompt, *images])
        st.subheader("The Response is")
        st.write(response.text)
        # image_data = response.text.split(",")[1] 
        # image_bytes = base64.b64decode(image_data)
        # st.write(image_bytes)
        # image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        # st.image(image, caption='Thumbnail Image')

    else:
        st.write("Please upload a video")
