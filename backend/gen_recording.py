from flask import Flask, request, jsonify
import requests


app = Flask(__name__)

url = "https://api.animo.video/v1/video/rendering"

# API Key (replace with your actual API key)
api_key = "YOUR_API_KEY"

# Request Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Request Body
data = {
    "code": """
from manim import *

class GenScene(Scene):
   def construct(self):
       axes = Axes(
           x_range=[-1, 6, 1],
           y_range=[-1, 11, 1],
           axis_config={"color": GREY},
       )
       labels = axes.get_axis_labels(x_label="x", y_label="y")
      
       line = axes.plot_line_graph(
           x_values=[0, 5],
           y_values=[0, 10],
           line_color=BLUE,
           vertex_dot_style={"fill_color": RED}
       )
      
       point_labels = VGroup(
           MathTex("(0, 0)").next_to(axes.c2p(0, 0), DOWN + LEFT),
           MathTex("(5, 10)").next_to(axes.c2p(5, 10), UP + RIGHT)
       )
      
       self.play(Create(axes), Write(labels))
       self.play(Create(line), Write(point_labels))
    """,
    "file_class": "GenScene",
    "project_name": "graph_rendering_project"
}

# Make the POST request
response = requests.post(url, headers=headers, json=data)

# Handle the response
if response.status_code == 200:
    result = response.json()
    print("Message:", result.get("message"))
    print("Video URL:", result.get("video_url"))
else:
    print(f"Error: {response.status_code}")
    print("Details:", response.text)







if __name__ == "__main__":
    app.run(debug=True)