import sounddevice as sd
import numpy as np
import threading
import asyncio
import edge_tts
import speech_recognition as sr
import subprocess
import os
import sys
import datetime
import pywhatkit
import pyjokes
import uuid
import psutil
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

recognizer = sr.Recognizer()
wake_up = False

# Load FLAN-T5 model
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

def speak(text):
    async def speak_async():
        filename = f"jarvis_output_{uuid.uuid4()}.mp3"
        communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
        await communicate.save(filename)
        try:
            import playsound
            playsound.playsound(filename)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    threading.Thread(target=lambda: asyncio.run(speak_async())).start()

def ask_ai(prompt):
    try:
        prompt = prompt.lower().strip().replace("hello jarvis", "")
        formatted_prompt = f"Answer this in simple terms: {prompt}"
        inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs, max_new_tokens=100)
        return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I couldn't process that."

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
                speak(ask_ai(text))
            elif text in ["stop", "exit", "quit"]:
                speak("Shutting down. Goodbye!")
                sys.exit()
            else:
                speak("I didn’t catch that. Could you repeat?")

def open_software(name):
    name = name.lower().strip()
    paths = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
    }
    for keyword, path in paths.items():
        if keyword in name:
            speak(f"Opening {keyword}.")
            subprocess.Popen(path)
            return
    if "play" in name:
        query = name.replace("play", "", 1)
        speak(f"Playing {query.strip()} on YouTube.")
        pywhatkit.playonyt(query.strip())
    else:
        speak(f"I couldn't find the software {name}. Please try again.")

def close_software(name):
    name = name.lower().strip()
    processes = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "code": "Code.exe"
    }
    for keyword, process in processes.items():
        if keyword in name:
            speak(f"Closing {keyword}.")
            os.system(f"taskkill /f /im {process}")
            return
    speak(f"No open software named {name} found.")

def tell_time():
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"It is {time_str}")

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is at {battery.percent} percent.")
        speak("Charger is connected." if battery.power_plugged else "Running on battery.")
    else:
        speak("Battery status not available.")

def system_shutdown():
    speak("Shutting down the system. Goodbye.")
    os.system("shutdown /s /t 5")

def system_restart():
    speak("Restarting your system.")
    os.system("shutdown /r /t 5")

def tell_joke():
    speak(pyjokes.get_joke())

def start_whistle_listener():
    print("👂 Listening for whistle to wake up...")
    global wake_up
    samplerate = 44100
    duration = 0.5
    min_freq = 1000
    max_freq = 3000
    threshold_db = -30

    def callback(indata, frames, time_info, status):
        global wake_up
        audio_data = indata[:, 0]
        fft_result = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1 / samplerate)
        magnitudes = 20 * np.log10(np.abs(fft_result) + 1e-6)

        dominant_freq = freqs[np.argmax(magnitudes)]
        dominant_db = np.max(magnitudes)

        if min_freq < dominant_freq < max_freq and dominant_db > threshold_db:
            print(f"🎵 Whistle detected! Freq: {dominant_freq:.0f} Hz, Vol: {dominant_db:.1f} dB")
            wake_up = True

    with sd.InputStream(callback=callback, channels=1, samplerate=samplerate, blocksize=int(samplerate * duration)):
        while not wake_up:
            sd.sleep(100)

def main():
    global wake_up
    boot_sound = "C:\\Users\\mudha\\Downloads\\boot_sound.mp3"
    if os.path.exists(boot_sound):
        import playsound
        playsound.playsound(boot_sound)

    speak("Initializing systems... Hello sir, I am JARVIS version 2 point O. Whistle to begin.")
    start_whistle_listener()
    if wake_up:
        speak("Good day sir. JARVIS online and ready.")
        listen_to_commands()

if __name__ == "__main__":
    main()
