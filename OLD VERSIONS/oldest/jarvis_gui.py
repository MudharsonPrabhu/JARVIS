import speech_recognition as sr
import pyttsx3
import os
import subprocess
import datetime
import psutil
import pywhatkit
import pyjokes
import sys
import threading
from tkinter import *

# Initialize Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "guy" in voice.name.lower():  # or "aria"
        engine.setProperty('voice', voice.id)
        break

recognizer = sr.Recognizer()

# Speak Function
def speak(text):
    output_box.insert(END, f"Jarvis: {text}\n")
    output_box.see(END)
    engine.say(text)
    engine.runAndWait()

# Command Functions
def open_software(name):
    name = name.lower().strip()
    if "chrome" in name:
        speak("Opening Chrome.")
        subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    elif "edge" in name:
        speak("Opening Microsoft Edge.")
        subprocess.Popen(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    elif "notepad" in name:
        speak("Opening Notepad.")
        subprocess.Popen("notepad.exe")
    elif "calculator" in name:
        speak("Opening Calculator.")
        subprocess.Popen("calc.exe")
    elif "paint" in name:
        speak("Opening Paint.")
        subprocess.Popen("mspaint.exe")
    elif "explorer" in name or "file" in name:
        speak("Opening File Explorer.")
        subprocess.Popen("explorer.exe")
    elif "vs code" in name or "code" in name:
        path = os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe")
        speak("Opening Visual Studio Code.")
        subprocess.Popen(path)
    elif "play" in name:
        query = name.replace("play", "", 1)
        speak(f"Playing {query.strip()} on YouTube.")
        pywhatkit.playonyt(query)
    else:
        speak(f"I couldn't find {name}.")

def tell_time():
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"It is {time_str}")

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is at {battery.percent} percent.")
        if battery.power_plugged:
            speak("Charger is connected.")
        else:
            speak("Running on battery.")
    else:
        speak("Battery info unavailable.")

def tell_joke():
    speak(pyjokes.get_joke())

def handle_command(text):
    output_box.insert(END, f"You: {text}\n")
    output_box.see(END)

    if text.startswith(("open", "launch")):
        open_software(text.replace("open", "").replace("launch", ""))
    elif text.startswith("close"):
        os.system(f"taskkill /f /im {text.replace('close', '').strip()}.exe")
        speak("Closed.")
    elif "time" in text:
        tell_time()
    elif "battery" in text:
        battery_status()
    elif "tell joke" in text:
        tell_joke()
    elif "your name" in text:
        speak("I am Jarvis, your assistant.")
    elif "who is god" in text:
        speak("Ajitheyyyy Kadavuleyyy!")
    elif text in ["stop", "exit", "quit"]:
        speak("Shutting down. Goodbye!")
        root.quit()
    else:
        speak("I didn’t catch that. Try again.")

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        speak("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="en-US").lower()
            handle_command(text)
        except:
            speak("Sorry, I didn’t catch that.")

def start_listening():
    threading.Thread(target=listen).start()

# GUI Setup
root = Tk()
root.title("Jarvis Assistant")
root.geometry("500x400")

Label(root, text="JARVIS - Simple Assistant", font=("Helvetica", 16)).pack(pady=10)
Button(root, text="Start Listening", font=("Helvetica", 14), command=start_listening).pack(pady=10)

output_box = Text(root, wrap=WORD, font=("Consolas", 12), height=15)
output_box.pack(padx=10, pady=10, fill=BOTH, expand=True)

speak("Jarvis is online. Press Start Listening to give a command.")
root.mainloop()