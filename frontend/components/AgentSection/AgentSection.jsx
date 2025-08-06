"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import styles from "./AgentSection.module.css";
import { useAIModel } from "../../app/AIModelContext";
import agentConfig from "../../data/agentConfig";
import ProjectCards from "../ProjectCards/ProjectCards";

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
  const [isLoading, setIsLoading] = useState(false);
  const [length, setLength] = useState("short");
  const [tone, setTone] = useState("neutral");
  const [audience, setAudience] = useState("general");
  const [copied, setCopied] = useState(false);

  const chatRef = useRef(null);
  const prevModelRef = useRef(model);
  const prevAgentTypeRef = useRef(agentType);

  useEffect(() => {
    setLang(detectLanguage());
  }, []);

  useEffect(() => {
    const savedHistory = localStorage.getItem(`${agentType}_history`);
    if (savedHistory && savedHistory !== "undefined") {
      setMessages(JSON.parse(savedHistory));
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

    if (trimmed.length < 8) {
      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          text: "Topic must be at least 8 characters",
        },
      ]);
      return;
    }

    setIsLoading(true);

    const body =
      agentType === "copywriter"
        ? {
            message: trimmed,
            model,
            length,
            tone,
            audience,
            chat_history: messages.map((msg) => ({
              role: msg.role === "agent" ? "assistant" : "user",
              content: msg.text,
            })),
            stream: true,
          }
        : {
            message: trimmed,
            model,
            chat_history: messages.map((msg) => ({
              role: msg.role === "agent" ? "assistant" : "user",
              content: msg.text,
            })),
          };

    try {
      const res = await fetch(`${apiUrl}/api/${agentType}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (data?.response) {
        const userMessage = { role: "user", text: trimmed };
        const agentMessage = {
          role: "agent",
          text: data.response,
          model,
        };

        if (agentType === "project" && Array.isArray(data.project_ids)) {
          agentMessage.projectIds = data.project_ids;
        }

        const updated = [...messages, userMessage, agentMessage];
        setMessages(updated);
        localStorage.setItem(`${agentType}_history`, JSON.stringify(updated));
      } else if (data?.error) {
        setMessages((prev) => [...prev, { role: "error", text: data.error }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: "Server error" }]);
    } finally {
      setIsLoading(false);
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

  const handleCopy = () => {
    const last = messages[messages.length - 1];
    if (last && last.role === "agent") {
      navigator.clipboard.writeText(last.text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
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

      {agentType === "copywriter" && (
        <div className={styles.copywriterParams}>
          <label>
            Length:
            <select value={length} onChange={(e) => setLength(e.target.value)}>
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </label>
          <label>
            Tone:
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="neutral">Neutral</option>
              <option value="formal">Formal</option>
              <option value="friendly">Friendly</option>
              <option value="funny">Funny</option>
            </select>
          </label>
          <label>
            Audience:
            <select value={audience} onChange={(e) => setAudience(e.target.value)}>
              <option value="general">General</option>
              <option value="business">Business</option>
              <option value="developers">Developers</option>
              <option value="students">Students</option>
            </select>
          </label>
        </div>
      )}

      <div className={styles.chatWrapper}>
        <div ref={chatRef} className={messages.length > 0 ? styles.chat : ""}>
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.role === "user" ? styles.user : styles.agent}>
              <strong>{msg.role === "user" ? "You: " : `AI (${msg.model || model}):`}</strong>
              {agentType === "project" && Array.isArray(msg.projectIds) && msg.projectIds.length > 0 && (
                <ProjectCards ids={msg.projectIds} />
              )}
              {msg.role === "user" ? (
                msg.text
              ) : (
                <>
                  <div className={styles.agentContent} dangerouslySetInnerHTML={{ __html: msg.text }} />
                  {agentType === "copywriter" && (
                    <button onClick={handleCopy} className={styles.copyButton}>
                      {copied ? "Copied!" : "Copy Code"}
                    </button>
                  )}
                </>
              )}
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
        <button
          onClick={sendMessage}
          className={`${styles.button} ${isLoading ? styles.loading : ""}`}
          disabled={input.trim().length < 3 || isLoading}
        >
          {isLoading ? "Sending" : "Send"}
          {isLoading && (
            <span className={styles.dots}>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
            </span>
          )}
        </button>
      </div>
    </section>
  );
}
