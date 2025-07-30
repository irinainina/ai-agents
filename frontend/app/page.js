import AgentSection from "@/components/AgentSection/AgentSection";
import AIModelSelector from "@/components/AIModelSelector/AIModelSelector";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.page}>
      <h1 className={styles.title}>AI Agents</h1>
      <AIModelSelector />

      <AgentSection agentType="project" />

      <AgentSection agentType="research" />

      <AgentSection agentType="welcome" />

      <AgentSection agentType="copywriter" />
    </main>
  );
}
