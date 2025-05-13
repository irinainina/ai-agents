"use client";

import { useAIModel } from "../../app/AIModelContext";
import styles from "./AIModelSelector.module.css";

export default function AIModelSelector() {
  const { model, setModel } = useAIModel();

  return (
    <div className={styles.selector}>
      <label htmlFor="model">AI Model:</label>
      <select id="model" value={model} onChange={(e) => setModel(e.target.value)}>
        <option value="gemma2-9b-it">Google - Gemma 2 (9B)</option>
        <option value="llama3-8b-8192">Meta - LLaMA 3 (8B)</option>
        <option value="llama3-70b-8192">Meta - LLaMA 3 (70B)</option>
        <option value="llama-3.1-8b-instant">Meta - LLaMA 3.1 (8B)</option>
        <option value="llama-guard-3-8b">Meta - LLaMA Guard (3-8B)</option>
        <option value="llama-3.3-70b-versatile">Meta - LLaMA 3.3 Versatile (70B)</option>
        <option value="meta-llama/llama-4-maverick-17b-128e-instruct">Meta - LLaMA 4 Maverick (17B)</option>
        <option value="whisper-large-v3">OpenAI - Whisper Large v3</option>
        <option value="whisper-large-v3-turbo">OpenAI - Whisper Large v3 Turbo</option>
        <option value="distil-whisper-large-v3-en">HuggingFace - Distil Whisper Large v3 (EN)</option>
      </select>
    </div>
  );
}
