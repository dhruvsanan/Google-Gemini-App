import os
import sys
import datetime
import openai
import dotenv
import streamlit as st
import tempfile
import moviepy.editor as mp

from audio_recorder_streamlit import audio_recorder

# import API key from .env file
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    """
    Transcribe the audio file at the specified path.

    :param file_path: The path of the audio file to transcribe
    :return: The transcribed text
    """
    with open(file_path, "rb") as audio_file:
        transcript = transcribe(audio_file)

    return transcript["text"]

def save_uploaded_video(video_file, file_path):

    with open(file_path, "wb") as f:
        f.write(video_file.read())

def main():
    """
    Main function to run the Whisper Transcription app.
    """
    st.title("Whisper Transcription")

    video_file = st.file_uploader("Upload a video file", type=["mp4"])

    if st.button("Transcribe"):
        audio_file = "temp_audio.wav"
        file_name = video_file.name
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        save_uploaded_video(video_file, file_path)
        video = mp.VideoFileClip(file_path)
        audio = video.audio
        audio.write_audiofile(audio_file)

        audio_file_path = max(
            [f for f in os.listdir(".") if f.startswith("temp")],
            key=os.path.getctime,
        )

        # Transcribe the audio file
        transcript_text = transcribe_audio(audio_file_path)

        # Display the transcript
        st.header("Transcript")
        st.write(transcript_text)


        # Provide a download button for the transcript
        st.download_button("Download Transcript", transcript_text)


if __name__ == "__main__":
    # Set up the working directory
    working_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(working_dir)

    # Run the main function
    main()