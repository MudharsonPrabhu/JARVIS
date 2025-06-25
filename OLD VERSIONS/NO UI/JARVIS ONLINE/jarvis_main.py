# jarvis_main.py

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
import requests
import numpy as np
import sounddevice as sd
import time
from collections import deque

# ---------- GLOBAL INITIALIZATION ----------
recognizer = sr.Recognizer()
mic_lock = threading.Lock()
wake_up = False

# ---------- AI RESPONSE FUNCTION ----------
def ask_ai(prompt, update_status=None):
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "phi-3",
            "messages": [
                {"role": "system", "content": "You are Jarvis, a helpful and intelligent assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        response = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"].strip()
            if update_status:
                update_status(f"🤖 JARVIS: {reply}")
            return reply
        else:
            error_msg = f"LM Studio Error: {response.text}"
            if update_status:
                update_status(f"❌ {error_msg}")
            return "Sorry, I couldn't process that request."
    except Exception as e:
        error_msg = f"AI Error: {str(e)}"
        if update_status:
            update_status(f"❌ {error_msg}")
        return "Something went wrong while connecting to local AI."

# ---------- SPEAK FUNCTION ----------
def speak(text):
    async def speak_async():
        import edge_tts
        import playsound
        filename = f"jarvis_output_{uuid.uuid4()}.mp3"
        try:
            mic_lock.acquire()
            communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
            await communicate.save(filename)
            playsound.playsound(filename, block=True)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            mic_lock.release()

    threading.Thread(target=lambda: asyncio.run(speak_async())).start()

# ---------- COMMAND HANDLERS ----------
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
        vscode_path = os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe")
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

# (You already have all these defined correctly — no need to copy again)

# ---------- LISTEN TO COMMANDS ----------
def listen_to_commands(update_status=None):
    with sr.Microphone() as source:
        local_recognizer = sr.Recognizer()
        local_recognizer.adjust_for_ambient_noise(source, duration=0.3)
        while True:
            try:
                if mic_lock.locked():
                    continue
                print("Command → Listening…")
                audio = local_recognizer.listen(source)
                text = local_recognizer.recognize_google(audio, language="en-US").lower().strip()
                print("Command →", text)
                if update_status:
                    update_status(f"🎤 Heard: {text}")
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
                cleaned = text.replace("hello jarvis", "").strip()
                answer = ask_ai(cleaned, update_status)
                speak(answer)
            elif text in ["stop", "exit", "quit"]:
                speak("Shutting down. Goodbye!")
                sys.exit()
            else:
                speak("I didn’t catch that. Could you repeat?")

# ---------- WHISTLE DETECTOR ----------
def detect_whistle(threshold_db=90, freq_low=1000, freq_high=4000):
    global wake_up

    def callback(indata, frames, stream_time, status):
        global wake_up
        if status: return
        if mic_lock.locked(): return
        try:
            audio = indata[:, 0]
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), d=1/44100)
            band_fft = fft[(freqs >= freq_low) & (freqs <= freq_high)]
            band_power = np.abs(band_fft) ** 2
            rms = np.sqrt(np.mean(band_power))
            db_spl = 20 * np.log10(rms / 2e-5 + 1e-12)
            print(f"📆 Sound Band RMS: {rms:.6f}, dB SPL: {db_spl:.2f}")

            if db_spl >= threshold_db:
                print("🎵 sound detected! Waking up...")
                wake_up = True

        except Exception as e:
            print(f"Callback error: {e}")

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=2048):
            print(f"🌍 Listening for a sound to wake up at ~{threshold_db} dB SPL...")
            while not wake_up:
                sd.sleep(200)
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        speak("Error starting audio stream. Please check your audio setup.")
        sys.exit(1)

# ---------- START FUNCTION FOR GUI ----------
def start_jarvis(update_status=None):
    import playsound

    def speak_and_update(text):
        if update_status:
            update_status(f"🤖 JARVIS: {text}")
        speak(text)

    
    speak_and_update("Initializing systems! Hello sir, I am Jarvis. Make sound to wake me up.")
    detect_whistle(threshold_db=80)
    speak_and_update("Good day sir! JARVIS online and ready.")
    listen_to_commands(update_status)

# ---------- RUN LOCALLY WITHOUT GUI ----------
if __name__ == "__main__":
    start_jarvis()
