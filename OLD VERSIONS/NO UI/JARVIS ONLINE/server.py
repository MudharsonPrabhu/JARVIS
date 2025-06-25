from flask import Flask, render_template, request, jsonify
import datetime
import psutil
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    message = request.json.get('message', '')
    try:
        lm_url = "http://localhost:1234/v1/chat/completions"  # LM Studio API
        payload = {
            "model": "phi3",  # Make sure this matches your model name in LM Studio
            "messages": [
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 400
        }
        headers = {"Content-Type": "application/json"}

        res = requests.post(lm_url, json=payload, headers=headers)
        res.raise_for_status()
        ai_reply = res.json()['choices'][0]['message']['content']

        return jsonify({'reply': ai_reply})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'reply': f"❌ Error: {str(e)}"})

@app.route('/status')
def get_status():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    date_str = now.strftime("%A, %d %B %Y")

    battery = psutil.sensors_battery()
    if battery:
        percent = f"{battery.percent}%"
        plugged = "⚡ Charging" if battery.power_plugged else "🔋 Not Charging"
    else:
        percent = "Unknown"
        plugged = "N/A"

    return jsonify({
        'time': time_str,
        'date': date_str,
        'battery': f"{percent} - {plugged}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Mobile accessible via LAN
