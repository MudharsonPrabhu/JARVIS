import requests

def ask_phi3(prompt):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": "phi3",  # Make sure this matches the actual model ID shown in LM Studio tab
        "messages": [
            {"role": "system", "content": "You are JARVIS, a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"
user_command = "What is a black hole?"  # Replace with real-time mic input
response = ask_phi3(user_command)

def speak(text):
    print(text)  # Replace with TTS code if needed

speak(response)
