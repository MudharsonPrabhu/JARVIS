from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Function to call LM Studio (Phi-3)
def ask_jarvis(prompt):
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
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"LM Studio Error: {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('message')
    reply = ask_jarvis(user_input)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
