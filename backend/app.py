from flask import Flask, request, jsonify

app = Flask(__name__)

import json
import requests


@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    
    # Simple logic to generate a response
    if messages:
        last_message = messages[-1]['content']
        response_message = f"Echo: {last_message}"
    else:
        response_message = "Hello! How can I assist you today?"

    return jsonify({"content": response_message})

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

@app.route('/query-llama', methods=['POST'])
def query_llama():
    try:
        user_prompt = request.json.get('prompt')
        if not user_prompt:
            return jsonify({"error": "Prompt is required"}), 400

        final_prompt = (
            f"Teach the user about \"{user_prompt}\". "
            "Explain the concepts in a sequential manner, after introducing a new part of the concept a specific deeper part about it, describe a in depth description of what the animation should look like. Keep the animation fairly simple and make sure your description descrebies clearly the shapes and figures that would be in the animation. Please also refer to any text that you would want in the animation in quotations, such as 'linear regression'. after doing this, continue with your explanation and repeat this if you see another animation needed"
        )


        data = {
            "model": "llama3.2",  
            "prompt": final_prompt,
            "stream": False  
        }

        # Forwarding request to Ollama
        response = requests.post(
            OLLAMA_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )

        # Return Ollama's response to the frontend
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)