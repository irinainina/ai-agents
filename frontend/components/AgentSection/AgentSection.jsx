"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./AgentSection.module.css";
import { useAIModel } from "../../app/AIModelContext";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

export default function AgentSection({ agentType, title, description }) {
  const { model } = useAIModel(); 

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const chatRef = useRef(null);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");

    try {
      const res = await fetch(`${apiUrl}/api/${agentType}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, model }),
      });

      const data = await res.json();
      if (data?.response) {
        setMessages((prev) => [...prev, { role: "agent", text: data.response }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: "Server error" }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className={styles.section}>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>

      <div ref={chatRef} className={messages.length > 0 ? styles.chat : ""}>
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === "user" ? styles.user : styles.agent}>
            <strong>{msg.role === "user" ? "You:" : msg.role === "agent" ? "AI:" : "Error:"}</strong> {msg.text}
          </div>
        ))}
      </div>

      <div className={styles.inputArea}>
        <input
          type="text"
          value={input}
          placeholder="Ask a question..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className={styles.input}
        />
        <button onClick={sendMessage} className={styles.button}>
          Send
        </button>
      </div>
    </section>
  );
}
