import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const fetchResponse = async (userMessage) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages: [...messages, { role: 'user', content: userMessage }] }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let content = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      content += decoder.decode(value);
      const parsed = content.split('\n\n').filter(Boolean).map(line => JSON.parse(line.replace('data: ', '')));
      setMessages([...messages, { role: 'user', content: userMessage }, ...parsed.map(p => ({ role: 'assistant', content: p.content }))]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      fetchResponse(input);
      setInput('');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="chat-box">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              <strong>{msg.role}:</strong> {msg.content}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
          />
          <button type="submit">Send</button>
        </form>
      </header>
    </div>
  );
}

export default App;
