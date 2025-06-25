import os
import sys
import subprocess
import datetime
import threading
import pyttsx3
import psutil
import pyjokes
import requests
import speech_recognition as sr
import playsound

# --------------- GLOBALS ---------------
engine = pyttsx3.init()
recognizer = sr.Recognizer()
mic_lock = threading.Lock()

# --------------- SPEAK FUNCTION ---------------
def speak(text):
    mic_lock.acquire()
    try:
        engine.say(text)
        engine.runAndWait()
    finally:
        mic_lock.release()

# --------------- AI CHAT (Local LM Studio) ---------------
def ask_ai(prompt):
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
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return "Sorry, I couldn't process that request."
    except Exception as e:
        return f"AI Error: {str(e)}"

# --------------- COMMAND FUNCTIONS ---------------
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
    else:
        speak(f"Software {name} not found.")

def close_software(name):
    name = name.lower().strip()
    if "chrome" in name:
        os.system("taskkill /f /im chrome.exe")
    elif "edge" in name:
        os.system("taskkill /f /im msedge.exe")
    elif "notepad" in name:
        os.system("taskkill /f /im notepad.exe")
    elif "calculator" in name:
        os.system("taskkill /f /im calc.exe")
    elif "code" in name:
        os.system("taskkill /f /im Code.exe")
    else:
        speak(f"No open software named {name} found.")

def tell_time():
    speak("It is " + datetime.datetime.now().strftime("%I:%M %p"))

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
    speak("Shutting down. Goodbye.")
    os.system("shutdown /s /t 5")

def system_restart():
    speak("Restarting your system.")
    os.system("shutdown /r /t 5")

def tell_joke():
    speak(pyjokes.get_joke())

# --------------- LISTEN AND PROCESS ---------------
def listen_and_process():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening now...")
        while True:
            try:
                print("Waiting for your command...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print("Heard:", command)

                if "open" in command or "launch" in command:
                    open_software(command.replace("open", "").replace("launch", ""))
                elif "close" in command:
                    close_software(command.replace("close", ""))
                elif "time" in command:
                    tell_time()
                elif "battery" in command:
                    battery_status()
                elif "tell joke" in command:
                    tell_joke()
                elif "shutdown" in command:
                    system_shutdown()
                elif "restart" in command:
                    system_restart()
                elif "your name" in command:
                    speak("I am Jarvis, your offline assistant.")
                elif "who is god" in command:
                    speak("Ajitheyyyy Kadavuleyyy!")
                elif any(word in command for word in ["what is", "who is", "explain"]):
                    reply = ask_ai(command)
                    speak(reply)
                elif command in ["stop", "exit", "quit"]:
                    speak("Shutting down. Goodbye!")
                    sys.exit()
                else:
                    speak("I didn’t understand. Please repeat.")
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
            except sr.RequestError:
                speak("Network error. I'm offline and using basic voice features.")
#wakeup detection
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
import numpy as np
import sounddevice as sd
# --------------- MAIN ---------------

def start_jarvis():
   # boot_sound = "C:\\Users\\mudha\\Downloads\\boot_sound.mp3"
    
   # if os.path.exists(boot_sound):
   #     playsound.playsound(boot_sound)
    
    speak("Initializing systems. Hello sir! I am Jarvis version 2 point o. Please make sound to wake me up.")

    while True:
        global wake_up
        wake_up = False
        detect_whistle(threshold_db=90, freq_low=1000, freq_high=4000)
        
        if wake_up:
            speak("Welcome Back Sir. System online. Awaiting your command.")
            try:
                listen_and_process()  # <- Your function to listen and handle commands
            except Exception as e:
                print("Error during command processing:", e)
                speak("Something went wrong while listening.")


if __name__ == "__main__":
    start_jarvis()
