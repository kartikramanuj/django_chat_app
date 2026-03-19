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
