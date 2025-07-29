"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import styles from "./AgentSection.module.css";
import { useAIModel } from "../../app/AIModelContext";
import agentConfig from "../../data/agentConfig";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;
const supportedLanguages = ["en", "ru", "uk"];

function detectLanguage() {
  const saved = localStorage.getItem("preferredLang");
  if (supportedLanguages.includes(saved)) return saved;

  const userLanguages = navigator.languages || [navigator.language];
  return (
    userLanguages.map((lang) => lang.split("-")[0]).find((baseLang) => supportedLanguages.includes(baseLang)) || "en"
  );
}

export default function AgentSection({ agentType }) {
  const { model } = useAIModel();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [lang, setLang] = useState("en");
  const chatRef = useRef(null);
  const prevModelRef = useRef(model);
  const prevAgentTypeRef = useRef(agentType);

  useEffect(() => {
    const initialLang = detectLanguage();
    setLang(initialLang);
  }, []);

  useEffect(() => {
    const savedHistory = localStorage.getItem(`${agentType}_history`);
    if (savedHistory && savedHistory !== "undefined") {
      const parsed = JSON.parse(savedHistory);
      setMessages(parsed);
    }
  }, [agentType]);

  useEffect(() => {
    if (prevModelRef.current !== model || prevAgentTypeRef.current !== agentType) {
      setMessages([]);
      localStorage.removeItem(`${agentType}_history`);
    }
    prevModelRef.current = model;
    prevAgentTypeRef.current = agentType;
  }, [model, agentType]);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const chat_history = messages.map((msg) => ({
      role: msg.role === "agent" ? "assistant" : "user",
      content: msg.text,
    }));

    try {
      const res = await fetch(`${apiUrl}/api/${agentType}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, model, chat_history }),
      });

      const data = await res.json();
      if (data?.response) {
        const updated = [...messages, { role: "user", text: trimmed }, { role: "agent", text: data.response }];
        setMessages(updated);
        localStorage.setItem(`${agentType}_history`, JSON.stringify(updated));
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: "Server error" }]);
    } finally {
      setInput("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  const handleNewChat = () => {
    setMessages([]);
    localStorage.removeItem(`${agentType}_history`);
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const config = agentConfig[agentType][lang];

  return (
    <section className={styles.section}>
      <div className={styles.imageWrapper}>
        <Image src={config.image} className={styles.image} width={700} height={467} alt="image" priority />
      </div>

      <div className={styles.titleWrapper}>
        <h2 className={styles.title}>{config.title}</h2>
        <button
          onClick={handleNewChat}
          className={`${styles.button} ${messages.length > 0 ? styles.active : styles.inactive}`}
        >
          New Chat
        </button>
      </div>
      <p className={styles.description}>{config.description}</p>

      <div className={styles.examples}>
        <h3 className={styles.questionsTitle}>{config.examplesTitle}</h3>
        {config.examples.map((ex, i) => (
          <button key={i} onClick={() => setInput(ex)} className={styles.exampleButton}>
            {ex}
          </button>
        ))}
      </div>

      <div className={styles.chatWrapper}>
        <div ref={chatRef} className={messages.length > 0 ? styles.chat : ""}>
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.role === "user" ? styles.user : styles.agent}>
              <strong>{msg.role === "user" ? "You:" : `AI (${msg.model || model}):`}</strong>
              {msg.role === "user" ? msg.text : <div dangerouslySetInnerHTML={{ __html: msg.text }} />}
            </div>
          ))}
        </div>
      </div>

      <div className={styles.inputArea}>
        <input
          type="text"
          value={input}
          placeholder={config.placeholder}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className={styles.input}
        />
        <button onClick={sendMessage} className={styles.button}>
          {config.send || "Send"}
        </button>
      </div>
    </section>
  );
}
