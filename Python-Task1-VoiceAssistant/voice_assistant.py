
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus


# Initialize Voice Assistant
engine = pyttsx3.init()
engine.setProperty("rate", 145)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()


# Function to speak
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# Function to listen through microphone
def listen():
    sample_rate = 16000
    duration = 5

    print("\nListening... Speak now!")

    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio_data = sr.AudioData(
            audio.tobytes(),
            sample_rate,
            2
        )

        command = recognizer.recognize_google(audio_data)

        print("You:", command)

        return command.lower()

    except sr.UnknownValueError:
        speak("Sorry, I could not understand.")
        return ""

    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return ""

    except Exception as error:
        print("Microphone Error:", error)
        speak("There was a microphone problem.")
        return ""


# Function to process user commands
def process_command(command):

    words = command.split()

    # Greeting
    if any(word in words for word in ["hello", "hi", "hey"]):
        speak("Hello! How can I help you?")

    # General conversation
    elif "how are you" in command:
        speak("I am doing great! Thank you for asking.")

    elif "what are you doing" in command:
        speak("I am waiting for your commands.")

    elif "had your lunch" in command or "have you eaten" in command:
        speak("I don't eat food, but thank you for asking!")

    # Time
    elif "time" in words:
        current_time = datetime.now().strftime("%I:%M %p")
        speak("The current time is " + current_time)

    # Date
    elif "date" in words or "today" in words:
        today = datetime.now().strftime("%d %B %Y")
        speak("Today's date is " + today)

    # Open Google
    elif "open google" in command or command == "google":
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    # Open YouTube
    elif "open youtube" in command or command == "youtube":
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    # Play music
    elif "play" in words and any(
        word in words for word in ["song", "songs", "music"]
    ):
        speak("Opening YouTube Music. Choose a song there.")
        webbrowser.open("https://music.youtube.com")

    # Google Search
    elif "search" in words:
        query = command.replace("search", "", 1).strip()

        if query:
            speak("Searching Google for " + query)

            search_url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )

            webbrowser.open(search_url)

        else:
            speak("Please tell me what to search.")

    # Exit
    elif "exit" in words or "stop" in words:
        speak("Goodbye! Have a nice day.")
        return False

    # Unknown command
    else:
        speak("Sorry, I don't know that command yet.")

    return True


# Main function
def main():

    speak("Hello! I am your voice assistant.")
    speak("How can I help you?")

    running = True

    while running:

        command = listen()

        if command:
            running = process_command(command)


# Program execution
if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nAssistant stopped.")
        speak("Goodbye!" )
