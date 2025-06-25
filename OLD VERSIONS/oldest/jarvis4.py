import customtkinter as ctk
import speech_recognition as sr
import asyncio
import edge_tts
import subprocess
import os
import sys
import psutil
import pywhatkit
import pyjokes
import threading

recognizer = sr.Recognizer()

# ----------------- TEXT-TO-SPEECH -----------------
def speak(text):
    async def speak_async():
        communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                os.write(1, chunk["data"])
    asyncio.run(speak_async())

# ----------------- CORE FUNCTIONS -----------------
def open_software(name):
    name = name.lower().strip()
    if "chrome" in name:
        speak("Opening Chrome.")
        subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    elif "notepad" in name:
        speak("Opening Notepad.")
        subprocess.Popen("notepad.exe")
    elif "calculator" in name:
        speak("Opening Calculator.")
        subprocess.Popen("calc.exe")
    elif "code" in name:
        speak("Opening VS Code.")
        subprocess.Popen(r"C:\Users\YourUsername\AppData\Local\Programs\Microsoft VS Code\Code.exe")
    elif "play" in name:
        song = name.replace("play", "").strip()
        speak(f"Playing {song}")
        pywhatkit.playonyt(song)
    else:
        speak("Software not found.")

def close_software(name):
    processes = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "code": "Code.exe"
    }
    for key, value in processes.items():
        if key in name:
            os.system(f"taskkill /f /im {value}")
            speak(f"Closed {key}")
            return
    speak("No such software open.")

def tell_time():
    from datetime import datetime
    time = datetime.now().strftime("%I:%M %p")
    speak(f"The time is {time}")

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is at {battery.percent} percent.")
    else:
        speak("Battery status not available.")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def shutdown():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 5")

def restart():
    speak("Restarting the system.")
    os.system("shutdown /r /t 5")

def exit_program():
    speak("Goodbye!")
    app.destroy()
    sys.exit()

# ----------------- COMMAND HANDLER -----------------
def handle_command(text):
    if "open" in text or "launch" in text:
        open_software(text)
    elif "close" in text:
        close_software(text)
    elif "time" in text:
        tell_time()
    elif "battery" in text:
        battery_status()
    elif "joke" in text:
        tell_joke()
    elif "shutdown" in text:
        shutdown()
    elif "restart" in text:
        restart()
    elif "exit" in text or "stop" in text:
        exit_program()
    else:
        speak("I didn’t catch that.")

# ----------------- LISTEN FUNCTION -----------------
def listen_loop():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        status_label.configure(text="Listening...", text_color="green")
        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                logbox.insert("end", f"You: {text}")
                if "hello jarvis" in text:
                    speak("JARVIS online. Ready for commands.")
                    status_label.configure(text="Responding...", text_color="blue")
                else:
                    handle_command(text)
            except Exception:
                continue

def start_jarvis():
    threading.Thread(target=listen_loop, daemon=True).start()

# ----------------- GUI -----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("JARVIS AI Assistant")
app.geometry("600x400")

title = ctk.CTkLabel(app, text="JARVIS - Voice Assistant", font=ctk.CTkFont(size=20, weight="bold"))
title.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Status: Idle", font=("Arial", 14))
status_label.pack(pady=5)

start_btn = ctk.CTkButton(app, text="Start Listening", command=start_jarvis)
start_btn.pack(pady=5)

exit_btn = ctk.CTkButton(app, text="Exit", command=exit_program)
exit_btn.pack(pady=5)

logbox = ctk.CTkTextbox(app, height=200, width=500)
logbox.pack(pady=10)
logbox.insert("end", "Log initialized...\n")

app.mainloop()
