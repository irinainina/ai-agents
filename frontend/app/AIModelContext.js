"use client";

import { createContext, useContext, useState } from "react";

const AIModelContext = createContext();

export function AIModelProvider({ children }) {
  const [model, setModel] = useState("llama3-8b-8192");

  return <AIModelContext.Provider value={{ model, setModel }}>{children}</AIModelContext.Provider>;
}

export function useAIModel() {
  return useContext(AIModelContext);
}
