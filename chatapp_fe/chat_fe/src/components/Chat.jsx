import { useEffect, useState, useRef } from 'react';

export default function Chat({ user }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const ws = useRef(null);

  useEffect(() => {
    async function loadMessages() {
      const res = await fetch(`http://localhost:8000/talk/messagehistory?receiver_id=4`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      const data = await res.json();
      setMessages(data);
    }
    loadMessages();

    ws.current = new WebSocket(`ws://localhost:8000/ws/chat/4/?token=${localStorage.getItem('token')}`);
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
