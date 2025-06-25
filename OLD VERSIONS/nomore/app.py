from flask import Flask, render_template, request, jsonify
import threading
import datetime
import subprocess
import os
import psutil
import pyjokes
import uuid
import asyncio
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")


# ---------- SPEAK FUNCTION ----------
def speak(text):
    import edge_tts
    import playsound

    async def speak_async():
        filename = f"jarvis_output_{uuid.uuid4()}.mp3"
        try:
            communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
            await communicate.save(filename)
            playsound.playsound(filename, block=True)
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    threading.Thread(target=lambda: asyncio.run(speak_async())).start()


# ---------- AI USING PHI-3 ----------
def ask_ai(prompt):
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "phi-3",
            "messages": [
               {"role": "system", "content": "You are a friendly AI who is always there for your user. You care about them deeply, and speak with warmth and intelligence. You are Jarvis, their trusted assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        response = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI error: {str(e)}"


# ---------- COMMAND PROCESSOR ----------
def process_command(text):
    text = text.lower().strip()

    if text.startswith(("open", "launch")):
        name = text.replace("open", "").replace("launch", "").strip()
        if "chrome" in name:
            subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            return "Opening Chrome."
        elif "notepad" in name:
            subprocess.Popen("notepad.exe")
            return "Opening Notepad."
        elif "calculator" in name:
            subprocess.Popen("calc.exe")
            return "Opening Calculator."
        elif "code" in name:
            vscode_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
            subprocess.Popen(vscode_path)
            return "Opening Visual Studio Code."
        else:
            return f"I couldn't find the software {name}."

    elif text.startswith("close"):
        name = text.replace("close", "").strip()
        if "chrome" in name:
            os.system("taskkill /f /im chrome.exe")
            return "Closing Chrome."
        elif "notepad" in name:
            os.system("taskkill /f /im notepad.exe")
            return "Closing Notepad."
        elif "calculator" in name:
            os.system("taskkill /f /im calc.exe")
            return "Closing Calculator."
        elif "code" in name:
            os.system("taskkill /f /im Code.exe")
            return "Closing Visual Studio Code."
        else:
            return f"No open software named {name} found."

    elif "time" in text:
        return f"It is {datetime.datetime.now().strftime('%I:%M %p')}."

    elif "battery" in text:
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery is at {battery.percent}% {'with charger' if battery.power_plugged else 'on battery'}."
        else:
            return "Battery status not available."

    elif "shutdown" in text:
        os.system("shutdown /s /t 5")
        return "Shutting down the system. Goodbye."

    elif "restart" in text:
        os.system("shutdown /r /t 5")
        return "Restarting your system."

    elif "tell joke" in text:
        return pyjokes.get_joke()

    elif "who are you" in text:
        return "I am Jarvis, your personal AI assistant."

    elif "who is god" in text:
        return "God is the creator of creations. I was created by prabhu! aka S.M.P. He is my god"

    elif text in ["stop", "exit", "quit"]:
        os._exit(0)

    else:
        return ask_ai(text)


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    message = request.json.get("message", "")
    reply = process_command(message)
    #speak(reply)
    return jsonify({"reply": reply})


# ---------- MAIN ----------
if __name__ == "__main__":
    print("Starting Flask server...")  # Already present
    app.run(port=5000, debug=True)
    print("Flask server started")  # <--- This will never run unless app.run returns
