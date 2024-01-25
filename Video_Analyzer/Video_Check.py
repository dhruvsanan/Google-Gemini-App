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

def save_uploaded_video(video_file, file_path):
    """
    Saves the uploaded video locally.

    Args:
        video_file (streamlit.UploadedFile): The uploaded video file.
        file_path (str): The path to the local file where the video should be saved.
    """

    with open(file_path, "wb") as f:
        f.write(video_file.read())

import cv2

def get_frames_n(video_file):
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
            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Resize the frame to half its original size
            frames.append(frame)
            # st.image(frame)
        frame_count += 1
    cap.release()
    return frames

import cv2

def get_frames_m(video_file):
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
            frame = cv2.pyrDown(frame)  # Downsample the frame
            frames.append(frame)
            # st.image(frame)
        frame_count += 1
    cap.release()
    return frames

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
            st.image(frame)
            frames.append(frame)
            # st.image(frame)
        frame_count += 1
    cap.release()
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
def create_image(data):
    image_bytes = base64.b64decode(data)
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    return image
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


st.set_page_config(page_title="Video Check")

st.header(" Video Check")

input = st.text_input("Input: ",key="input")
video_file = st.file_uploader("Upload a video", type=["mp4"])

# st.write(video_file._file_urls.upload_url)

submit=st.button("Tell me about the Video")
input_prompt4 = """
imagine the continuation of the images as a video. what do you observe from this video?
"""

if submit: 
    if video_file is not None:
        file_name = video_file.name
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        save_uploaded_video(video_file, file_path)
        frames=get_frames(file_path)
        # st.success(f"Video saved to {file_path}")


        # cap = cv2.VideoCapture(file_path)
        # # Get the frame rate of the video
        # frame_rate = cap.get(cv2.CAP_PROP_FPS)

        # # Calculate the interval between frames to save
        # frame_interval = frame_rate

        # # Create a list to store the frames
        # frames = []

        # # Loop over the frames in the video
        # frame_count =0
        # while cap.isOpened():
        #     # Read the next frame
        #     ret, frame = cap.read()

        #     # If the frame is empty, break out of the loop
        #     if not ret:
        #         break
            

        #     # Check if the frame should be saved
        #     if frame_count % frame_interval == 0:
        #         # Convert the frame to a NumPy array
        #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #         # Add the frame to the list
        #         frames.append(frame)

        #     # Increment the frame count
        #     frame_count += 1

        # # Close the video capture
        # cap.release()


        # # Create a directory to save the frames
        # output_dir = "output_frames"

        # Save the frames to the directory
        # for i, frame in enumerate(frames):
        #     cv2.imwrite(f"{output_dir}/frame_{i}.jpg", frame)
        #     st.image(frame)
        images = handle_image_uploads(frames)
        # Display a success message
        # st.success(f"{len(frames)} frames saved")
        # st.write(images)
        response = image_model.generate_content([input_prompt4,input, *images])
        st.subheader("The Response is")
        st.write(response.text)
        # image_data = response.text.split(",")[1] 
        # image_bytes = base64.b64decode(image_data)
        # st.write(image_bytes)
        # image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        # st.image(image, caption='Thumbnail Image')

    else:
        st.write("Please upload a video")
