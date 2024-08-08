import streamlit as st
import os
import requests
from dotenv import load_dotenv
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import subprocess
import tempfile
import pyaudio
import wave
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Get the API keys from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
hf_token = os.getenv("HUGGINGFACE_API_KEY")

# API URL and headers for Hugging Face
API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
headers = {"Authorization": f"Bearer {hf_token}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        st.error(f"Error: {response.status_code}")
        st.error(response.json())  # Print the response JSON for debugging
    response.raise_for_status()  # Ensure we raise an error for bad responses
    return response.content

def speech_to_text():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5  # You can adjust this value

    p = pyaudio.PyAudio()

    st.write("Please speak after clicking the 'Start Recording' button.")
    if st.button("Start Recording"):
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        st.write("Recording...")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        st.write("Recording finished.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded audio to a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            wf = wave.open(tmpfile.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            audio_file = tmpfile.name

        # Use speech recognition on the temporary file
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            st.write("You said: " + text)
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            st.write("Could not request results; {0}".format(e))
            return ""
        finally:
            # Clean up the temporary file
            os.unlink(audio_file)

    return ""

def generate_content(text):
    # Configure the Generative AI model with API key
    genai.configure(api_key=api_key)

    # Initialize the GenerativeModel
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generate content based on the text read from the file
    response = model.generate_content(
        f"You are a sophisticated voice assistant AI named Wall-E. Your role is to provide clear, concise, and helpful responses based on the following input. Ensure your responses are accurate, friendly, and professional. The input is: {text}"
    )

    return response.text

def generate_audio_from_text(text):
    # Generate audio from text using Hugging Face API
    audio_bytes = query({"inputs": text})

    # Save the raw audio bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as tmpfile:
        tmpfile.write(audio_bytes)
        raw_audio_file = tmpfile.name

    # Convert raw audio to WAV using ffmpeg
    wav_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    subprocess.run([
        'ffmpeg', '-y', '-i', raw_audio_file, '-f', 'wav', wav_audio_file
    ], check=True)

    # Clean up raw audio file
    os.unlink(raw_audio_file)

    return wav_audio_file

def main():
    st.title("Wall-E: Your Virtual Assistant")
    st.write("Welcome! I'm here to assist you. What would you like to do?")

    text = speech_to_text()
    
    if text:
        with st.spinner("Generating response..."):
            content = generate_content(text)
        
        st.write("Wall-E's response:")
        st.write(content)
        
        with st.spinner("Generating audio..."):
            audio_filename = generate_audio_from_text(content)
        
        st.audio(audio_filename, format="audio/wav")
        
        # Clean up the audio file after playing
        os.unlink(audio_filename)

    # Add a text input for manual queries
    user_input = st.text_input("Or type your question here:")
    if user_input:
        with st.spinner("Generating response..."):
            content = generate_content(user_input)
        
        st.write("Wall-E's response:")
        st.write(content)
        
        with st.spinner("Generating audio..."):
            audio_filename = generate_audio_from_text(content)
        
        st.audio(audio_filename, format="audio/wav")
        
        # Clean up the audio file after playing
        os.unlink(audio_filename)

    # Add a sidebar with additional information
    st.sidebar.title("About Wall-E")
    st.sidebar.write("Wall-E is a sophisticated virtual assistant powered by advanced AI technologies. It can understand your speech, generate helpful responses, and even speak back to you!")

    # Add a fun fact or tip in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Did you know?")
    st.sidebar.write("Wall-E's name is inspired by the lovable robot from the Pixar movie. Just like the movie character, our Wall-E is here to help and make your life easier!")

if __name__ == "__main__":
    main()