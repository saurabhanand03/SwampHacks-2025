from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

OLLAMA_API_URL = "https://api.ollama.com/v1/generate"
OLLAMA_API_KEY = "your_ollama_api_key"  # Replace with your actual Ollama API key

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])

    # Extract the last user message
    if messages:
        last_message = messages[-1]['content']
    else:
        last_message = "Hello! How can I assist you today?"

    # Make a request to the Ollama API
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': last_message,
        'model': 'llama-2-7b-chat'  # Specify the model you want to use
    }
    response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)
    response_data = response.json()
    response_message = response_data['choices'][0]['text']

    return jsonify({"content": response_message})

if __name__ == '__main__':
    app.run(debug=True)