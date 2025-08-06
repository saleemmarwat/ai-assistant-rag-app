'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '../../lib/supabaseClient';
//import ChatSidebar from '../../components/ChatSidebar';
import type { User } from '@supabase/supabase-js';

// ✅ Chat type for supabase 'chats' table
type Chat = {
  id: number;
  user_id: string;
  query: string;
  answer: string;
  created_at: string;
};

export default function RagPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [uploading, setUploading] = useState(false);
  //const [chatHistory, setChatHistory] = useState<Chat[]>([]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      const sessionUser = data?.session?.user;
      if (!sessionUser) {
        router.push('/');
      } else {
        console.log("✅ Logged in as:", sessionUser.id);
        setUser(sessionUser);
        //fetchChatHistory(sessionUser.id);
      }
    });
  }, [router]); // ✅ Added 'router' to dependency array

  const fetchChatHistory = async (userId: string) => {
    const { data, error } = await supabase
      .from('chats')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (!error && data) setChatHistory(data as Chat[]);
  };

  const handleUpload = async () => {
    if (!file || !user) return;

    console.log("📤 Uploading file for user:", user.id);
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', user.id);

    try {
      const res = await fetch('http://localhost:8000/ingest', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      console.log('✅ Upload response:', data);
      if (!res.ok) {
        alert(`❌ Upload failed: ${data.message || res.statusText}`);
      } else {
        alert(data.message);
      }
    } catch (err) {
      console.error('❌ Upload error:', err);
      alert('Upload failed. Check console for details.');
    }

    setUploading(false);
  };

  const handleQuery = async () => {
    if (!query || !user) return;

    console.log("💬 Asking question as:", user.id);

    const res = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, user_id: user.id }),
    });

    const data = await res.json();
    setAnswer(data.answer);
    fetchChatHistory(user.id);
  };

  const logout = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* <ChatSidebar chat={chatHistory} /> */}
      <main style={{ flex: 1, padding: 40, position: 'relative' }}>
        <div style={{
          position: 'absolute',
          top: 10,
          right: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 12
        }}>
          <span>Hello, {user?.email}</span>
          <button onClick={logout} style={{
            padding: '4px 10px',
            backgroundColor: '#e63946',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            cursor: 'pointer'
          }}>
            Logout
          </button>
        </div>

        <h2 style={{ marginTop: 40 }}>🧠 AI Assistant</h2>
        <h3>Upload a PDF and start asking questions!</h3>
        <input type='file' onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={handleUpload} style={{ marginLeft: 10 }}>
          {uploading ? 'Uploading...' : 'Upload & Ingest'}
        </button>

        <br /><br />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder='Ask a question...'
          style={{ width: '60%', padding: 8 }}
        />
        <button onClick={handleQuery} style={{ marginLeft: 10 }}>
          Ask
        </button>

        <p style={{ marginTop: 20 }}><strong>Answer:</strong> {answer}</p>
      </main>
    </div>
  );
}
