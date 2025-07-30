import styles from "./ProjectCards.module.css";
import projects from "../../../backend/data/projects.json";

export default function ProjectCards({ ids }) {
  const items = ids.map((id) => projects.find((p) => p.id === id)).filter(Boolean);

  if (items.length === 0) return null;

  return (
    <div className={styles.cards}>
      {items.map((project) => (
        <div key={project.id} className={styles.card}>
          <img src={project.image} alt={project.name} />
          <h3>{project.name}</h3>
          <p><em>{project.slogan}</em></p>
          <p>{project.timeline} • {project.industry.join(", ")}</p>
          <p>{project.description}</p>
          <a href={project.link} target="_blank" rel="noopener noreferrer">View case study →</a>
        </div>
      ))}
    </div>
  );
}
