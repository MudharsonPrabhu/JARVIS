import speech_recognition as sr
import asyncio
import edge_tts
import datetime
import subprocess
import os
import sys
import psutil  
import pywhatkit
import pyjokes
import threading
import uuid

# ---------- GLOBAL INITIALIZATION ----------
recognizer = sr.Recognizer()

# ---------- SPEAK FUNCTION USING EDGE-TTS ----------
def speak(text):
    async def speak_async():
        filename = f"jarvis_output_{uuid.uuid4()}.mp3"
        communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
        await communicate.save(filename)
        try:
            import playsound
            playsound.playsound(filename, block=True)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    threading.Thread(target=lambda: asyncio.run(speak_async())).start()

# ---------- SOFTWARE HANDLERS ----------
def open_software(name):
    name = name.lower().strip()
    if "chrome" in name:
        speak("Opening Chrome.")
        subprocess.Popen(r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    elif "edge" in name:
        speak("Opening Microsoft Edge.")
        subprocess.Popen(r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
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
        speak("Opening Visual Studio Code.")
        vscode_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
        subprocess.Popen(vscode_path)
    elif "play" in name:
        query = name.replace("play", "", 1)
        speak(f"Playing {query.strip()} on YouTube.")
        pywhatkit.playonyt(query.strip())
    else:
        speak(f"I couldn't find the software {name}. Please try again.")

def close_software(name):
    name = name.lower().strip()
    if "chrome" in name:
        speak("Closing Chrome.")
        os.system("taskkill /f /im chrome.exe")
    elif "edge" in name:
        speak("Closing Microsoft Edge.")
        os.system("taskkill /f /im msedge.exe")
    elif "notepad" in name:
        speak("Closing Notepad.")
        os.system("taskkill /f /im notepad.exe")
    elif "calculator" in name:
        speak("Closing Calculator.")
        os.system("taskkill /f /im calc.exe")
    elif "code" in name:
        speak("Closing Visual Studio Code.")
        os.system("taskkill /f /im Code.exe")
    else:
        speak(f"No open software named {name} found.")

# ---------- EXTRA FUNCTIONS ----------
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
        speak("Battery status not available.")

def system_shutdown():
    speak("Shutting down the system. Goodbye.")
    os.system("shutdown /s /t 5")

def system_restart():
    speak("Restarting your system.")
    os.system("shutdown /r /t 5")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

# ---------- COMMAND LISTENER ----------
def listen_to_commands():
    with sr.Microphone() as source:
        local_recognizer = sr.Recognizer()
        local_recognizer.adjust_for_ambient_noise(source, duration=0.3)
        while True:
            try:
                print("Command → Listening…")
                audio = local_recognizer.listen(source)
                text = local_recognizer.recognize_google(audio, language="en-US").lower()
                print("Command →", text)
            except:
                continue

            if text.startswith(("open", "launch")):
                open_software(text.replace("open", "").replace("launch", ""))
            elif text.startswith("close"):
                close_software(text.replace("close", ""))
            elif "time" in text:
                tell_time()
            elif "battery" in text:
                
                battery_status()
            elif "tell joke" in text:
                tell_joke()
            elif "shutdown" in text:
                system_shutdown()
            elif "restart" in text:
                system_restart()
            elif "your name" in text:
                speak("I am Jarvis, your personal AI assistant.")
            elif "who is god" in text:
                speak("Ajjeeeetheeeeee Kadaaavuuuuleeeeyyy!")
            elif text in ["stop", "exit", "quit"]:
                speak("Shutting down. Goodbye!")
                sys.exit()
            else:
                speak("I didn’t catch that. Could you repeat?")

# ---------- WAKE-UP LISTENER ----------
def listen_and_respond():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        while True:
            try:
                print("Waiting for wake word: 'Hello Jarvis' …")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio, language="en-US").lower()
                print("Heard →", text)
                if "hello jarvis" in text:
                    speak("Good day sir. JARVIS online and ready.")
                    listen_to_commands()
            except Exception as e:
                print("Error:", str(e))
                continue

# ---------- MAIN ----------
if __name__ == "__main__":
    boot_sound = "C:\\Users\\mudha\\Downloads\\boot_sound.mp3"
    if os.path.exists(boot_sound):
        import playsound
        playsound.playsound(boot_sound)
    speak("Initializing systems... Hello sir, I am JARVIS version 2 point O. Say 'Hello Jarvis' to begin.")
    listen_and_respond()
