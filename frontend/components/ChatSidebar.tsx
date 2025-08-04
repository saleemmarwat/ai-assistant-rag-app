export default function ChatSidebar({ chat }: { chat?: any[] }) {
  return (
    <aside style={{ width: 300, background: '#f4f4f4', padding: 20, height: '100vh', overflowY: 'auto' }}>
      <h3 style={{ marginBottom: 16 }}>🕘 Chat History</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {(!chat || chat.length === 0) && <li>No history yet</li>}
        {chat?.map((c, i) => (
          <li key={i} style={{ marginBottom: 16 }}>
            <div><strong>Q:</strong> {c.question}</div>
            <div><strong>A:</strong> {c.answer}</div>
            <hr />
          </li>
        ))}
      </ul>
    </aside>
  );
}
