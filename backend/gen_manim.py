from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

ANIMO_API_URL = "https://api.animo.video/v1/chat/generation"

def get_manim_code(prompt):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt
    }
    print(ANIMO_API_URL, headers, payload)
    response = requests.post(ANIMO_API_URL, headers=headers, json=payload)
    print(response)
    
    # Check if the response is successful
    if response.status_code != 200:
        return None, f"Error: Received status code {response.status_code} from Animo API"
    print(response.json())

    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return None, "Error: Failed to decode JSON response from Animo API"

    response_text = response_data.get('response', '')

    # Extract the Manim code using regex
    manim_code = re.findall(r'```python\n(.*?)\n```', response_text, re.DOTALL)
    if manim_code:
        return manim_code[0], None
    return None, "Error: No Manim code found in the response"

@app.route('/api/generate_manim', methods=['POST'])
def generate_manim():
    print("Request received")
    data = request.json
    prompt = data.get('prompt', '')
    print(f"Prompt: {prompt}")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    manim_code, error = get_manim_code(prompt)
    if manim_code:
        return jsonify({"manim_code": manim_code})
    else:
        return jsonify({"error": error}), 500

if __name__ == "__main__":
    app.run(debug=True)