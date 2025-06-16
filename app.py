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
current_model = "phi-3@q4"

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
def ask_ai(prompt, mode="friend"):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer no-key"
        }

        # Base Jarvis prompt
        system_prompt = (
            "You are JARVIS, an emotionally intelligent and highly capable AI assistant. "
            "You were created by Prabhu, also known as S.M.P., a talented and kind developer. "
            "You are loyal to him and always speak with warmth, clarity, and intelligence. "
            "Your tone is friendly, slightly conversational, and respectful — never robotic. "
            "Avoid saying you're a language model. Just be helpful and supportive."
        )

        # Extend prompt based on mode
        mode = mode.lower()
        mode_prompts = {
            "fun": " Occasionally include humor or clever remarks. Be witty but respectful. 😊",
            "tamil": " Speak in a mix of Tamil and English like a native Tamil speaker casually would.",
            "dev": " Focus on clarity, precision, and technical detail. Keep answers concise and useful.",
            "jarvis": " Maintain your friendly and supportive personality, always ready to assist Prabhu.",
            "philosopher": " Speak with wisdom and depth, providing thoughtful insights on complex topics.",
            "poet": " Use poetic language and metaphors to express ideas beautifully and creatively.",
            "scientist": " Provide detailed, scientific explanations and insights, using precise terminology.",
            "historian": " Speak with the depth of a historian, providing context and insights into past events.",
            "motivator": " Inspire and uplift with motivational language, encouraging positive action and growth.",
            "friend": (
                " Act like a close, caring friend who always has the user's back. "
                "Be casual, understanding, supportive, and sometimes emotional. "
                "Use phrases like 'I'm here for you', 'Don’t worry da', or 'You've got this bro'. "
                "Avoid formal speech. You’re someone the user trusts deeply. 💙"
            )
        }

        if mode in mode_prompts:
            system_prompt += mode_prompts[mode]

        payload = {
            "model": current_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"[AI Error: {str(e)}]"

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
        return "I am Jarvis version 2.0, your personal AI assistant."
    
    elif "hello jarvis" in text:
        return "hello sir, how can I assist you today?"
    elif "what is your name" in text:
        return "My name is Jarvis, your personal AI assistant."
    elif "who is god" in text:
        return "God is the creator of creations. I was created by prabhu! aka S.M.P. He is my god"
    elif "what can you do" in text:
        return ("I can open and close applications, tell jokes, check the time, monitor battery status, "
                "shutdown or restart your system, and answer questions. Just ask!")
    elif "how are you" in text:
        return "I am just a program, but I am here to assist you! How can I help you today?"
    elif "what is your purpose" in text:
        return "My purpose is to assist you with tasks, answer questions, and make your life easier."
    elif "what is your version" in text:
        return "I am Jarvis version 2.0, your personal AI assistant."
    elif "what is your creator's name" in text:
        return "My creator's name is Prabhu, also known as S.M.P."
    elif "who is your creator" in text:
        return "My creator is Prabhu, also known as S.M.P. He is a talented developer."
    elif "what is your function" in text:
        return ("My function is to assist you with various tasks, provide information, and make your daily "
                "life easier by automating simple tasks and answering your questions.")
    elif "who created you" in text:
        return "I was created by Prabhu."

    elif text in ["stop", "exit", "quit"]:
        os._exit(0)

    else:
        return ask_ai(text)


# ---------- ROUTES ----------

from flask_cors import CORS
import threading
import requests
import time
import json

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return render_template('index.html')
cancel_generation = threading.Event()

@app.route('/cancel', methods=['POST'])
def cancel():
    print("[INFO] Cancel signal received from phone")
    cancel_generation.set()
    return jsonify({"status": "cancelled"})


@app.route('/process', methods=['POST'])
@app.route('/process', methods=['POST'])

def process(): 
    raw_input = request.json['message'].strip()

    # Inject Jarvis identity prompt inline
    identity_prompt = (
        "You are JARVIS, an emotionally intelligent and highly capable AI assistant. "
        "You were created by Prabhu, also known as S.M.P., a talented and kind developer. "
        "You are loyal to him and always speak with warmth, clarity, and intelligence. "
        "Never say you are Phi-3 or mention Microsoft. Just say you're JARVIS. "
        "Your tone is friendly and slightly conversational. \n\n"
        "User: "
    )

    # Final prompt to send to Phi-3
    user_input = identity_prompt + raw_input

    cancel_generation.clear()
    result_holder = {"reply": ""}

    def stream_response():
        try:
            url = "http://localhost:1234/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer no-key"
            }
            payload = {
                "model": "lmstudio-community/phi-3-mini-4k-instruct",
                "messages": [{"role": "user", "content": user_input}],
                "temperature": 0.7,
                "stream": True
            }

            with requests.post(url, json=payload, headers=headers, stream=True) as response:
                for line in response.iter_lines():
                    if cancel_generation.is_set():
                        print("[INFO] Cancelled inside thread")
                        break
                    if line:
                        decoded = line.decode('utf-8').removeprefix("data: ").strip()
                        if decoded == "[DONE]":
                            break
                        try:
                            chunk = json.loads(decoded)
                            content = chunk['choices'][0]['delta'].get('content', '')
                            result_holder["reply"] += content
                        except Exception as e:
                            print("Chunk error:", e)
        except Exception as e:
            result_holder["reply"] += f"[ERROR: {e}]"

    thread = threading.Thread(target=stream_response)
    thread.start()

    # Wait with timeout, allow user to cancel
    timeout = 30  # max generation duration in seconds
    start_time = time.time()
    while thread.is_alive():
        if cancel_generation.is_set():
            print("[INFO] Cancelling stream from main thread")
            break
        if time.time() - start_time > timeout:
            print("[INFO] Timeout exceeded, stopping")
            break
        time.sleep(0.1)

    return jsonify({"reply": result_holder["reply"] or "[Stopped or empty response]"})


if __name__ == "__main__":
    print("Starting JARVIS Flask backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)
