import requests 
import re
import time

ANIMO_CHAT_URL = "https://api.animo.video/v1/chat/generation"
API_KEY = "YOUR_API_KEY"  # Replace with your actual key

def get_manim_code(prompt: str, max_retries: int = 1):
    """
    Sends a prompt to Animo's chat/generation endpoint and attempts to
    extract Manim code (fenced with ```...```) from the response text.

    Returns:
        (code_str, error_message)
         - code_str: string containing the first fenced code block
         - error_message: None if success, or a string describing the error
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                ANIMO_CHAT_URL, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()  # Raises HTTPError if status >= 400
            break
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} of {max_retries} timed out. Retrying...")
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            return None, f"Error: {e}"
    else:
        return None, f"Error: Request timed out after {max_retries} attempts"

    # Use response.text instead of JSON
    raw_text = response.text

    # Find code fenced with triple backticks
    code_matches = re.findall(r'```(.*?)```', raw_text, re.DOTALL)

    if not code_matches:
        return None, "Error: No code fences found in the response"

    return code_matches[0], None

# --------------------------------------------------------
# Simple test block
# --------------------------------------------------------
if __name__ == "__main__":
    test_prompt = "Show a blue circle being created and then transforming into a red square."

    code, error = get_manim_code(test_prompt)
    if error:
        print("Failed to retrieve Manim code:", error)
    else:
        print("Manim code retrieved:\n", code)