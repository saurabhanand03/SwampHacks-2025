from flask import Flask, request, jsonify
import requests
import re
import time

app = Flask(__name__)

ANIMO_API_URL = "http://127.0.0.1:8080/v1/chat/generation"

def get_manim_code(prompt):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'messages': [{'role': 'user', 'content': prompt}],
        'engine': 'openai'  # or 'anthropic' depending on your preference
    }
    print(f"Sending request to {ANIMO_API_URL} with headers {headers} and payload {payload}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(ANIMO_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            break  # Exit the loop if the request is successful
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} of {max_retries} timed out. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
        except requests.exceptions.RequestException as e:
            return None, f"Error: An error occurred while making the request to Animo API: {e}"
    else:
        return None, "Error: Request to Animo API timed out after multiple attempts"

    # Check if the response is successful
    if response.status_code != 200:
        return None, f"Error: Received status code {response.status_code} from Animo API"

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
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    manim_code, error = get_manim_code(prompt)
    if manim_code:
        return jsonify({"manim_code": manim_code})
    else:
        return jsonify({"error": error}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)