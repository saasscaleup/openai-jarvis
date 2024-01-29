import numpy as np
import openai
import random
from scipy.io.wavfile import write
import sounddevice as sd
import pyttsx3
import os

# Set your OpenAI API key here
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Global variable to store audio data
# audio = []

# Adjectives to generate random names for voices
adjectives = ["beautiful", "sad", "mystical", "serene", "whispering", "gentle", "melancholic"]
nouns = ["sea", "love", "dreams", "song", "rain", "sunrise", "silence", "echo"]

#initializing pytts for text to speech output
engine = pyttsx3.init()

# Set speech speed rate 
engine.setProperty('rate', 185)

def change_voice(engine, language, gender='VoiceGenderFemale'):

    try:
        for voice in engine.getProperty('voices'):
            if language in voice.languages and gender == voice.gender:
                engine.setProperty('voice', voice.id)
                return True

        raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))
    except:
        print("Language not found")

change_voice(engine, "en_US", "VoiceGenderFemale")

def generate_random_name():
    # to generate random unique names for the audio voice recordings
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adjective} {noun}"

def new_record_audio():
    # to record audio as wav file
    print("Recording... Press 's' to stop.")
    fs = 48000
    seconds = 6
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1,blocking=True)
    sd.wait()  # Wait until recording is finished
    audio_name = generate_random_name()
    write(f'./voices/{audio_name}.wav', fs, myrecording)  # Save as WAV file 
    print("Recording stopped.")
    return f'./voices/{audio_name}.wav'
    
def speech_to_text(audio_path):
    print ("entered transcribe", "./"+audio_path)
    audio_file= open(audio_path, "rb")
    print(audio_file)
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)
    return transcript['text']

def text_to_speech(response):
    # to generate the final output voice from text
    engine.say(response)
    engine.runAndWait()


def openai_chat_send(transcript):

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": transcript}
    ]
    print("Transcript:")
    print(transcript)
    # Make the API call for gpt AI
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message["content"]


def main():
    while True:
        print("Press 's' to stop recording and transcribe the audio.")
        # Start recording live voice input
        recorded_audio_path = new_record_audio()

        print("Recording stopped. Transcribing audio...")
        
        # Save the recorded audio as a WAV file
        print("Recorded audio saved to:", recorded_audio_path)
        print("----end---")

        # Transcribe the audio
        transcript = speech_to_text(recorded_audio_path)

        # send user input to openai chatgpt
        response = openai_chat_send(transcript)

        # Print the assistant's response
        print("Assistant:", response)
        
        # Convert output to voice
        text_to_speech(response)

        # # Ask whether to continue or stop
        # user_choice = input("Continue? (y/n): ")
        # if user_choice.lower() == "n":
        #     print("Glad to help bye!")
        #     break  # Exit the loop if the user doesn't want to continue

if __name__ == "__main__":
    main()
