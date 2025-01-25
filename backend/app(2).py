from flask import Flask, request, Response
from flask_cors import CORS
from llama_cpp import Llama
import json

app = Flask(__name__)
CORS(app)

# Initialize Llama model
# Make sure to download the Llama model file and update the path accordingly
llm = Llama(model_path="./models/llama-2-7b-chat.gguf", n_ctx=2048)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])

    # Convert messages to Llama format
    prompt = "".join([f"{m['role']}: {m['content']}\n" for m in messages])
    prompt += "assistant: "

    def generate():
        for token in llm(prompt, max_tokens=200, stop=["user:", "\n"], stream=True):
            content = token["choices"][0]["text"]
            yield f"data: {json.dumps({'content': content})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)