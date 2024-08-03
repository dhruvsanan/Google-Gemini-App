import openai
import datetime
import cv2
from PIL import Image
import google.generativeai as genai
import tempfile
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

image_model = genai.GenerativeModel("gemini-1.5-pro")


def save_uploaded_video(video_file, file_path):
    with open(file_path, "wb") as f:
        f.write(video_file.read())


def get_frame(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count_s = 0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    new_frame_interval = int(frame_count / 15)
    total_length_seconds = frame_count / frame_rate
    if total_length_seconds > 60:
        # Video is more than 1 minute long, so delete the first 10 seconds and last 10 seconds
        start_frame = frame_rate * 10  # First 10 seconds
        end_frame = frame_count - (frame_rate * 10)  # Last 10 seconds
    else:
        # Video is not more than 1 minute long, so don't delete any frames
        start_frame = 0
        end_frame = frame_count
    frame_interval = frame_rate
    if new_frame_interval > frame_interval:
        frame_interval = new_frame_interval
    frames = []
    st.write(new_frame_interval)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    cap.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count_s % frame_interval == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Check if the payload size of the frame exceeds the limit
            payload_size = len(frame.tobytes())
            st.image(frame)
            if payload_size > 4194304:
                # The payload size exceeds the limit, so we cannot send this frame
                continue
            frames.append(frame)
            # st.image(frame)
        frame_count_s += 1
    cap.release()
    st.write(len(frames))
    return frames


def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = 0
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_length_seconds = cap.get(cv2.CAP_PROP_FRAME_COUNT) / frame_rate
    if total_length_seconds > 60:
        # Video is more than 1 minute long, so delete the first 10 seconds and last 10 seconds
        start_frame = int(frame_rate * 10)  # First 10 seconds
        end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) -
                        (frame_rate * 10))  # Last 10 seconds
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) - (frame_rate * 20)
        new_frame_interval = int(total_frames / 16)
    else:
        # Video is not more than 1 minute long, so don't delete any frames
        start_frame = 0
        end_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        new_frame_interval = int(end_frame / 15)
    frame_interval = frame_rate
    if new_frame_interval > frame_interval:
        frame_interval = new_frame_interval
    frames = []
    st.write(new_frame_interval)
    frame_count = start_frame  # Initialize frame_count with start_frame
    st.write(frame_count)
    while cap.isOpened() and frame_count < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            payload_size = len(frame.tobytes())
            st.image(frame)
            if payload_size > 4194304:
                continue  # Skip frame if payload size exceeds limit
            frames.append(frame)
        frame_count += 1
        # st.write(frame_count)
    cap.release()
    st.write(len(frames))
    return frames


def handle_image_uploads(uploaded_file):
    # Initialize an array to store the images
    images = []

    # Iterate over the uploaded files
    for idx, file in enumerate(uploaded_file):
        # Create a unique variable name for the image
        image_variable_name = f"image{idx+1}"

        # Open the image using OpenCV
        image = Image.fromarray(file)

        # Assign the image to the unique variable
        globals()[image_variable_name] = image

        # Add the image to the array
        images.append(image)

    # Return the array of images
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
st.header("Video Analyser Check")

question = st.text_input("Input: ", key="input")
video_file = st.file_uploader("Upload a video", type=["mp4"])

# st.write(video_file._file_urls.upload_url)

submit = st.button("Tell me about the Video")
input_prompt = """
imagine the continuation of the images as a video.
Hey Act Like a skilled or very experience Video Analyzer.
Train your self with only the video and the transcript provided.
your task is to answer the question only based on the transcript and the video that you recieved.
Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. 
However, you are talking to a non-technical audience, so be sure to break down complicated concepts and 
strike a friendly and converstional tone. 
If the answer to the question is out of the transcript or the video, you may ignore it or say sorry! I am unable answer it.
Remember you only have to answer to question if the information is available in either transcript or video. Do not provide details of anything else including video and transcript."""

if submit:
    if video_file is not None:
        file_name = video_file.name
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        save_uploaded_video(video_file, file_path)
        frames = get_frames(file_path)

        images = handle_image_uploads(frames)
        transcript_text = transcribe_audio(file_path)
        st.write(transcript_text)
        response = image_model.generate_content(
            [transcript_text, *images, input_prompt, question])
        st.subheader("The Response is")
        st.write(response.text)
        # image_data = response.text.split(",")[1]
        # image_bytes = base64.b64decode(image_data)
        # st.write(image_bytes)
        # image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        # st.image(image, caption='Thumbnail Image')

    else:
        st.write("Please upload a video")
