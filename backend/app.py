import re
import requests
from flask import Flask, request, jsonify

# Import the Python function from gen_recording.py
from gen_recording import render_manim_code

app = Flask(__name__)

# 1) An endpoint that orchestrates the entire pipeline
@app.route("/api/full_pipeline", methods=["POST"])
def full_pipeline():
    """
    Expects a JSON body like:
      {
        "prompt": "some subject you want to explain, e.g. 'Neural networks'"
      }

    """
    req_data = request.json or {}
    user_prompt = req_data.get("prompt")
    if not user_prompt:
        return jsonify({"error": "No 'prompt' provided"}), 400

    # ------------------------------------------------
    # 1) Call gen_explanation's /query-llama endpoint
    # ------------------------------------------------
    # (Assuming gen_explanation runs on port 5000)
    explanation_url = "http://127.0.0.1:5000/query-llama"
    explanation_resp = requests.post(explanation_url, json={"prompt": user_prompt})
    if explanation_resp.status_code != 200:
        return jsonify({
            "error": f"Call to gen_explanation failed with {explanation_resp.status_code}",
            "details": explanation_resp.text
        }), 500

    explanation_json = explanation_resp.json()
    full_text = explanation_json.get("response", "")

    # ------------------------------------------------
    # 2) Extract everything between triple backticks
    #    i.e. the "animation descriptions"
    # ------------------------------------------------
    # Use a regex that grabs anything between ``` ... ```
    snippets = re.findall(r'```(.*?)```', full_text, re.DOTALL)

    # We'll store results for each snippet
    video_results = []


    for snippet in snippets:
        manim_url = "http://127.0.0.1:5001/api/generate_manim"
        manim_resp = requests.post(manim_url, json={"prompt": snippet})
        if manim_resp.status_code != 200:
            video_results.append({
                "snippet": snippet,
                "error": f"gen_manim returned {manim_resp.status_code}",
                "details": manim_resp.text
            })
            continue

        manim_json = manim_resp.json()
        if "manim_code" not in manim_json:
            video_results.append({
                "snippet": snippet,
                "error": manim_json.get("error", "No manim_code in response")
            })
            continue

        # 3b) We have the generated Manim code. Now pass it to render_manim_code (locally imported from gen_recording)
        manim_code = manim_json["manim_code"]
        record_result = render_manim_code(manim_code, project_name="my_cool_project")

        # record_result might look like:
        #   {
        #       "message": "...",
        #       "video_url": "...",
        #       "error": None / "some error"
        #   }

        # Let's store that in our final results
        video_results.append({
            "snippet": snippet,
            "manim_code": manim_code,
            "render_result": record_result
        })


    return jsonify({"videos": video_results}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5002)
