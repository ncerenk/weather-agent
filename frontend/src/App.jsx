import { useState } from "react";
import ReactMarkdown from "react-markdown";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState(null);

  const [sessionId] = useState(() =>
    crypto.randomUUID()
  );

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          current_user: null,
          session_id: sessionId,
        }),
      });

      const data = await res.json();

      setTokenUsage({
        input: data.input_tokens,
        output: data.output_tokens,
        total: data.total_tokens,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Hata oluştu",
        },
      ]);
    }

    setLoading(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div style={{ padding: "40px", maxWidth: "900px", margin: "0 auto" }}>
      <h1
  style={{
    textAlign: "center",
    marginBottom: "20px",
    fontSize: "42px",
  }}
>
  🌤️ Weather Multi-Agent
     </h1>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "12px",
          height: "400px",
          overflowY: "auto",
          padding: "20px",
          marginBottom: "15px",
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              justifyContent:
                msg.role === "user"
                  ? "flex-end"
                  : "flex-start",
              marginBottom: "15px",
            }}
          >
            <div
              style={{
                maxWidth: "70%",
                padding: "12px",
                borderRadius: "12px",
                backgroundColor:
                  msg.role === "user" ? "#4A90E2" : "#F1F1F1",
                color: msg.role === "user" ? "white" : "black",
                
              }}
            >
              <ReactMarkdown>
               {msg.content}
             </ReactMarkdown>
            </div>
          </div>
        ))}

        {loading && <p>Yükleniyor...</p>}
      </div>

     {tokenUsage && (
  <div
    style={{
      display: "flex",
      gap: "12px",
      marginBottom: "15px",
    }}
  >
    <div
      style={{
        flex: 1,
        padding: "10px",
        borderRadius: "10px",
        background: "#f3f4f6",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "12px", color: "#666" }}>
        📥 Input
      </div>
      <div style={{ fontSize: "20px", fontWeight: "bold" }}>
        {tokenUsage.input}
      </div>
    </div>

    <div
      style={{
        flex: 1,
        padding: "10px",
        borderRadius: "10px",
        background: "#f3f4f6",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "12px", color: "#666" }}>
        📤 Output
      </div>
      <div style={{ fontSize: "20px", fontWeight: "bold" }}>
        {tokenUsage.output}
      </div>
    </div>

    <div
      style={{
        flex: 1,
        padding: "10px",
        borderRadius: "10px",
        background: "#e8f4ff",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "12px", color: "#666" }}>
        🧮 Total
      </div>
      <div style={{ fontSize: "20px", fontWeight: "bold" }}>
        {tokenUsage.total}
      </div>
    </div>
  </div>
)}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Mesaj yaz..."
          style={{
            width: "80%",
            padding: "12px",
            marginRight: "10px",
          }}
        />

        <button
  type="submit"
  style={{
    padding: "12px 20px",
    border: "none",
    borderRadius: "10px",
    backgroundColor: "#4A90E2",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "0.2s",
  }}
>
  Gönder
</button>
      </form>
    </div>
  );
}

export default App;