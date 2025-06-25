import speech_recognition as sr
import datetime
import subprocess
import os
import sys
import psutil
import pywhatkit
import pyjokes
import threading
import uuid
import asyncio
import numpy as np
import sounddevice as sd
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from collections import deque
import time

# ---------- GLOBAL INITIALIZATION ----------
recognizer = sr.Recognizer()
wake_up = False
mic_lock = threading.Lock()

# ---------- LOAD FLAN-T5 MODEL ----------
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

# ---------- AI RESPONSE FUNCTION ----------
def ask_ai(prompt):
    try:
        prompt = prompt.lower().strip()
        formatted_prompt = f"Answer this in simple terms: {prompt}"
        inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs, max_new_tokens=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I couldn't process that."

# ---------- SPEAK FUNCTION USING EDGE-TTS ----------
def speak(text):
    async def speak_async():
        import edge_tts
        import playsound
        filename = f"jarvis_output_{uuid.uuid4()}.mp3"

        try:
            mic_lock.acquire()  # 🔒 Pause mic detection
            communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
            await communicate.save(filename)
            playsound.playsound(filename, block=True)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            mic_lock.release()  # 🔓 Resume mic detection

    threading.Thread(target=lambda: asyncio.run(speak_async())).start()

# ---------- SOFTWARE HANDLERS ----------
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
                text = local_recognizer.recognize_google(audio, language="en-US").lower().strip()
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
                speak("Ajitheyyyy Kadavuleyyy!")
            elif any(word in text for word in ["explain", "what is", "who is"]):
                answer = ask_ai(text)
                speak(answer)
            elif text in ["stop", "exit", "quit"]:
                speak("Shutting down. Goodbye!")
                sys.exit()
            else:
                speak("I didn’t catch that. Could you repeat?")

# ---------- TRIPLE CLAP DETECTOR ----------
def detect_triple_clap(threshold_db=20.0, time_window=2.0, min_interval=0.1):
    global wake_up
    clap_times = deque(maxlen=3)  # Store timestamps of potential claps

    def callback(indata, frames, time, status):
        global wake_up
        if status:  # Check for any stream status errors
            print(f"Stream status: {status}")
            return
        if mic_lock.locked():
            return  # Skip detection while TTS is speaking

        try:
            volume_norm = np.linalg.norm(indata) * 10
            current_time = time.time()  # Use Python's time instead of PortAudio's time

            if volume_norm > threshold_db:
                clap_times.append(current_time)
                print(f"👏 Clap detected! Volume: {round(volume_norm, 1)} dB at {current_time}")

                # Check if we have three claps within the time window
                if len(clap_times) == 3:
                    first_clap_time = clap_times[0]
                    last_clap_time = clap_times[-1]
                    if last_clap_time - first_clap_time <= time_window:
                        intervals = [clap_times[i+1] - clap_times[i] for i in range(len(clap_times)-1)]
                        if all(interval >= min_interval for interval in intervals):
                            print("👏👏👏 Triple clap detected!")
                            wake_up = True
        except Exception as e:
            print(f"Callback error: {e}")

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=1024):
            print("👂 Listening for triple clap to wake up...")
            while not wake_up:
                sd.sleep(200)
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        speak("Error starting audio stream. Please check your audio setup.")
        sys.exit(1)

# ---------- MAIN ----------
if __name__ == "__main__":
    boot_sound = "C:\\Users\\mudha\\Downloads\\boot_sound.mp3"
    if os.path.exists(boot_sound):
        import playsound
        playsound.playsound(boot_sound)
    speak("Initializing systems... Clap three times to wake me up.")
    detect_triple_clap()
    speak("Good day sir. JARVIS online and ready.")
    listen_to_commands()