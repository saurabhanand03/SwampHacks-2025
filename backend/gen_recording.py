import requests

ANIMO_URL = "https://api.animo.video/v1/video/rendering"
API_KEY = "YOUR_API_KEY"

def render_manim_code(manim_code: str, project_name: str = "my_cool_project"):
    """
    Renders the given Manim code via the Animo API and returns a dict with:
      - "message": The status message from Animo
      - "video_url": The video URL if successful, or None otherwise
      - "error": Error string if the request fails
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "code": manim_code,
        "file_class": "GenScene",   # or however your Manim code defines the scene class
        "project_name": project_name
    }

    try:
        response = requests.post(ANIMO_URL, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        return {
            "message": None,
            "video_url": None,
            "error": f"Network/request error: {str(e)}"
        }

    if response.status_code == 200:
        result = response.json()
        return {
            "message": result.get("message"),
            "video_url": result.get("video_url"),
            "error": None
        }
    else:
        return {
            "message": None,
            "video_url": None,
            "error": f"Animo returned {response.status_code}: {response.text}"
        }


