from flask import Flask, request, jsonify

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

if __name__ == '__main__':
    app.run(debug=True)