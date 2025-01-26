import React, { useState } from "react";
import { Send } from "lucide-react";
import "./ChatInterface.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = { type: "user", text: inputMessage };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5002/api/full_pipeline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: inputMessage }),
      });

      console.log(response);

      if (!response.ok) {
        throw new Error("Chat API request failed");
      }

      const data = await response.json();
      console.log(data);

      const newMessages = data.map((item) => {
        if (item.text) {
          return { type: "cpu", text: item.text };
        } else if (item.manim_video && item.manim_video.video_url) {
          return { type: "cpu", video_url: item.manim_video.video_url };
        } else {
          return item;
        }
      });

      setMessages((prevMessages) => [...prevMessages, ...newMessages]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        type: "error",
        text: "An unexpected error occurred while processing your request. Please attempt to resend.",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h1 className="chat-title">InSight</h1>
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            {msg.text}
            {msg.video_url && (
              <video width="600" controls>
                <source src={msg.video_url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        ))}
        {isLoading && <div className="message cpu">Typing...</div>}
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
          placeholder="Type a message..."
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
        >
          <Send size={24} />
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
