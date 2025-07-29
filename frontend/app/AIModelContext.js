"use client";

import { createContext, useContext, useState, useEffect } from "react";
const AIModelContext = createContext();

export function AIModelProvider({ children }) {  
  const [model, setModel] = useState("");
  
  useEffect(() => {
    const selectedModel = localStorage.getItem("selected-model");
    if (selectedModel) {
      setModel(selectedModel);
    } else {
      setModel("llama3-8b-8192");
    }
  }, []);
  
  const updateModel = (newModel) => {
    setModel(newModel);
    localStorage.setItem("selected-model", newModel);
  }

  if (!model) return null;

  return <AIModelContext.Provider value={{ model, setModel: updateModel }}>{children}</AIModelContext.Provider>;
}

export function useAIModel() {
  return useContext(AIModelContext);
}
