// vite.config.js (or vite.config.ts if using TypeScript)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});

// main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// App.jsx
import { useState } from 'react';
import Chat from './components/Chat';
import Login from './components/Login';
import Signup from './components/Signup';

function App() {
  const [user, setUser] = useState(null);
  return user ? <Chat user={user} /> : <Login onLogin={setUser} />;
}

export default App;

// components/Login.jsx
import { useState } from 'react';

export default function Login({ onLogin }) {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  async function login() {
    const res = await fetch('http://localhost:8000/account/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    });
    const data = await res.json();
    if (data.access) {
      localStorage.setItem('token', data.access);
      const profile = await fetch('http://localhost:8000/account/user', {
        headers: { Authorization: `Bearer ${data.access}` },
      });
      const userData = await profile.json();
      onLogin(userData);
    }
  }

  return (
    <div>
      <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="Phone" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
      <button onClick={login}>Login</button>
    </div>
  );
}

// components/Chat.jsx
import { useEffect, useState, useRef } from 'react';

export default function Chat({ user }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const ws = useRef(null);

  useEffect(() => {
    async function loadMessages() {
      const res = await fetch(`http://localhost:8000/talk/messagehistory?receiver_id=5`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      const data = await res.json();
      setMessages(data);
    }
    loadMessages();

    ws.current = new WebSocket(`ws://localhost:8000/ws/chat/5/?token=${localStorage.getItem('token')}`);
    ws.current.onmessage = e => {
      const msg = JSON.parse(e.data);
      setMessages(prev => [...prev, msg]);
    };
    return () => ws.current.close();
  }, []);

  function sendMessage() {
    ws.current.send(JSON.stringify({ message: text }));
    setText('');
  }

  return (
    <div>
      <h2>Chat with user #5</h2>
      <div style={{ height: '300px', overflowY: 'scroll' }}>
        {messages.map((msg, idx) => (
          <div key={idx}><strong>{msg.sender_id === user.id ? 'You' : 'Them'}:</strong> {msg.message}</div>
        ))}
      </div>
      <input value={text} onChange={e => setText(e.target.value)} placeholder="Type message..." />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

// components/Signup.jsx (optional, can be similar to Login with POST to /account/signup)
