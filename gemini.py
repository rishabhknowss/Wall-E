import os
import google.generativeai as genai


genai.configure(api_key="AIzaSyCETUgcbYjurqRZQFu-ee8Z8kz-5fZHs1M")


# Initialize the GenerativeModel
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the filename
filename = "recognized_text.txt"

# Read the text from the file
try:
    with open(filename, "r") as file:
        text = file.read()
except FileNotFoundError:
    print(f"File {filename} not found.")
    text = ""  # Set text to empty if file is not found

# Generate content based on the text read from the file
response = model.generate_content(
    f"You are Wall-E, an AI fun chatbot. You have to give right and good responses based on the following input: {text}"
)

print(response.text)
