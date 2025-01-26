from flask import Flask, request, jsonify
import requests
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

LLM = "GPT4.0" # OLLAMA

app = Flask(__name__)

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

if LLM == "OLLAMA":
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
elif LLM == "GPT4.0":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

def generate_explanation(user_prompt):
    print("Generating explanation for prompt:", user_prompt)  # Debug print
    final_prompt = (
        f""""Your role is half teacher and half animation description creator. You must teach the user about \"{user_prompt}\". "
        "Explain the concepts in a sequential manner. For each new concept, provide a detailed explanation and then, if there is a clear visual opportunity to enhance understanding, describe a separate animation that visualizes the concept. Place each of the animation descriptions in between ***begin*** and ***end***. only the animation descriptiosn go inbetween.  explanations should not appear in the animation description parts of your response.\n\n"
        "Treat every animation as standalone and independent, ensuring no assumptions about memory or continuity between animations. Every animation must focus on visual specificity and simplicity. For any text, labels, coordinate points, or specific numbers representing size appearing in the animation, enclose them in quotations, such as 'linear regression', 'circle', '5', or '(0, 0)'. Avoid ambiguous or abstract descriptions and ensure the animations are clear and easy to interpret.\n\n"
        "Each animation should explicitly describe the following in a concise, effective, and descriptive way:\n"
        "- Shapes (e.g., circles, squares, or arrows).\n"
        "- Their positioning relative to each other.\n"
        "- Any movement or transformation (e.g., lines forming, shapes moving).\n"
        "- Text content, labels, coordinate points, and size values, all enclosed in quotations, such as 'label', 'circle', '10', or '(5, 10)'.\n\n"
        "- For the animation description, avoid multiple long label names to avoid overlap. 
        "Avoid unnecessary details or redundant phrasing. For example, use concise terms such as 'a straight line' rather than 'a smooth and continuous line with no visible gaps or jumps'. Focus on clarity and brevity while maintaining specificity.\n\n"
        "Do not include measurements of line segments or shapes unless they are explicitly labeled in the animation description. The primary goal is to create specific and actionable visual instructions without overcomplicating the descriptions. Avoid actions like 'pointing' at elements or introducing randomization. Instead, describe the visual elements with precision, emphasizing their purpose in the animation.\n\n"
        "After completing the animation description, continue explaining the concept in detail. If another animation is necessary, repeat this process, ensuring each animation is independent and isolated. Do not reference or rely on previous animations, as all animations are created individually without memory or continuity."
        "Keep the descriptions of the animations seperate from the content explanation, The content explanation should lead into the animation description but the animation description should contain only visual detials nothing conceptual."
        "Conceptual detials remain in the content explanations" """
    )

    if LLM == "OLLAMA":
        print("Sending request to OLLAMA API...")
        data = {
            "model": "llama3.1:8b",  
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
    
    elif LLM == "GPT4.0":
        print("Sending request to OpenAI API...")  # Debug print
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": final_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="gpt-4o-mini-2024-07-18",
        )

        print("Received response from OpenAI API")  # Debug print
        if response:
            return response.choices[0].message.content;
        else:
            print("Error response from OpenAI API")  # Debug print
            raise Exception("Failed to get response from OpenAI API")

@app.route('/query-llama', methods=['POST'])
def query_llama():
    print("Received request")  # Debug print
    try:
        user_prompt = request.json.get('prompt')
        if not user_prompt:
            print("No prompt provided")  # Debug print
            return jsonify({"error": "Prompt is required"}), 400
        print(f"Received prompt: {user_prompt}")  # Debug print

        result = generate_explanation(user_prompt)
        print("Generated explanation successfully")  # Debug print
        return jsonify({"explanation": result})

    except Exception as e:
        print("Exception occurred:", str(e))  # Debug print
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")  # Debug print
    app.run(debug=True)