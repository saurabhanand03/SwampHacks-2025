import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# 1) Import the Python function from gen_explanation.py
from gen_explanation import generate_explanation

# 2) Import the Python function from gen_recording.py
from gen_recording import render_manim_code

# 3) Import the Python function from gen_manim.py
#    so we don't need to call the /api/generate_manim endpoint
from gen_manim import get_manim_code

app = Flask(__name__)
CORS(app)

@app.route("/api/full_pipeline", methods=["POST"])
def full_pipeline():
    """
    Expects JSON body like:
      {
        "prompt": "some subject you want to explain, e.g. 'Neural networks'"
      }
    """
    print("Received request")
    req_data = request.json or {}
    user_prompt = req_data.get("prompt")
    if not user_prompt:
        return jsonify({"error": "No 'prompt' provided"}), 400
    print(f"Received prompt: {user_prompt}")

    try:
        # ------------------------------------------------
        # 1) Call gen_explanation directly
        # ------------------------------------------------
        full_text = generate_explanation(user_prompt)
        print("Generated explanation successfully")

        # ------------------------------------------------
        # 2) Extract everything between ***begin*** and ***end***
        # ------------------------------------------------
        # Each snippet is an "animation description"
        snippets = re.split(r'(\*\*\*begin\*\*\*.*?\*\*\*end\*\*\*)', full_text, flags=re.DOTALL)

        # ------------------------------------------------
        # 3) For each snippet, get Manim code, then render it
        # ------------------------------------------------
        result = []
        for snippet in snippets:
            if snippet.startswith("***begin***") and snippet.endswith("***end***"):
                # Extract the snippet between ***begin*** and ***end***
                snippet = snippet[len("***begin***"):-len("***end***")].strip()

                # Generate Manim code by calling get_manim_code directly
                manim_code, error = get_manim_code(snippet)
                
                if error:
                    # If get_manim_code fails, store the error
                    result.append({"error": error})
                else:
                    # Render that Manim code into a video
                    record_result = render_manim_code(manim_code, project_name="my_cool_project")
                    result.append({"manim_video": record_result})
            else:
                # Add the text snippet as is
                result.append({"text": snippet})

        # Return JSON for all parts
        return jsonify(result)

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run the orchestrator on port 5002
    app.run(debug=True, port=5002)