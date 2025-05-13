import AgentSection from "@/components/AgentSection/AgentSection";
import AIModelSelector from "@/components/AIModelSelector/AIModelSelector";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.page}>
      <h1 className={styles.title}>AI Agents</h1>
      <AIModelSelector/>
      <AgentSection
        agentType="welcome"
        title="Welcome Agent"
        description="Answers general questions and routes users to the right section based on their intent (employer, client, programmer)."
      />

      <AgentSection
        agentType="project"
        title="Project Agent"
        description="Provides information about portfolio projects, technical details, and implementation approaches."
      />

      <AgentSection
        agentType="career"
        title="Career Agent"
        description="Describes skills, experience, and helps assess fit for job positions."
      />

      <AgentSection
        agentType="client"
        title="Client Agent"
        description="Explains services, pricing, delivery process, and generates client proposals."
      />

      <AgentSection
        agentType="research"
        title="Research Agent"
        description="Answers technical questions and explains trends, comparisons, and industry insights."
      />
    </main>
  );
}
