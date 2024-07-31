import os
import requests
from dotenv import load_dotenv
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import subprocess

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
        print(f"Error: {response.status_code}")
        print(response.json())  # Print the response JSON for debugging
    response.raise_for_status()  # Ensure we raise an error for bad responses
    return response.content

def speech_to_text(filename):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        
        # Save the text to a file
        with open(filename, "w") as file:
            file.write(text)
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        text = ""
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        text = ""

    return text

def generate_content(text):
    # Configure the Generative AI model with API key
    genai.configure(api_key=api_key)

    # Initialize the GenerativeModel
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generate content based on the text read from the file
    response = model.generate_content(
        f"You are a sophisticated voice assistant AI named Wall-E. Your role is to provide clear, concise, and helpful responses based on the following input. Ensure your responses are accurate, friendly, and professional. The input is: {text}"
    )

    print(response.text)

    return response.text

def generate_audio_from_text(text):
    # Generate audio from text using Hugging Face API
    audio_bytes = query({"inputs": text})

    # Save the raw audio bytes to a file
    raw_audio_file = "raw_audio_output"
    with open(raw_audio_file, "wb") as f:
        f.write(audio_bytes)

    # Convert raw audio to WAV using ffmpeg
    wav_audio_file = "bark_generation.wav"
    subprocess.run([
        'ffmpeg', '-y', '-i', raw_audio_file, '-f', 'wav', wav_audio_file
    ], check=True)

    # Clean up raw audio file
    os.remove(raw_audio_file)

    return wav_audio_file

def play_audio(filename):
    # Load and play the generated audio file
    audio = AudioSegment.from_file(filename, format="wav")
    play(audio)

def main():
    text_filename = "recognized_text.txt"
    
    # Convert speech to text
    text = speech_to_text(text_filename)
    
    # Generate content if text is not empty
    if text:
        content = generate_content(text)
        
        # Generate audio from the content
        audio_filename = generate_audio_from_text(content)
        
        # Play the generated audio
        play_audio(audio_filename)
    else:
        print("No text was generated from speech. Skipping content generation.")

if __name__ == "__main__":
    main()
