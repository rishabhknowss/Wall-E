import speech_recognition as sr

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
    with open("recognized_text.txt", "w") as file:
        file.write(text)
except sr.UnknownValueError:
    print("Sorry, I could not understand the audio.")
except sr.RequestError as e:
    print("Could not request results; {0}".format(e))
