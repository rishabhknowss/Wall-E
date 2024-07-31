import os
from dotenv import load_dotenv
import speech_recognition as sr
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

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

def main():
    filename = "recognized_text.txt"
    
    # Convert speech to text
    text = speech_to_text(filename)
    
    # Generate content if text is not empty
    if text:
        generate_content(text)
    else:
        print("No text was generated from speech. Skipping content generation.")

if __name__ == "__main__":
    main()
