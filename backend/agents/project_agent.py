import os
import json
import numpy as np
from pathlib import Path
from langdetect import detect, DetectorFactory
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

DetectorFactory.seed = 0

class ProjectAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.default_model = default_model
        self.projects = self._load_projects()
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.project_embeddings = self._generate_project_embeddings()

    def _load_projects(self):
        data_dir = Path(__file__).parent.parent / "data"
        file_path = data_dir / "projects.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project data: {e}")
            return []

    def _detect_language(self, text):
        try:
            return detect(text)
        except:
            return "en"

    def _generate_project_embeddings(self):
        texts = [proj.get("name", "") + " " + proj.get("text", "") for proj in self.projects]
        return self.embedder.encode(texts, convert_to_tensor=True)

    def _find_similar_projects(self, query, top_n=3):
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        similarities = cosine_similarity(
            [query_embedding.cpu().numpy()],
            self.project_embeddings.cpu().numpy()
        )[0]
        top_indices = np.argsort(similarities)[::-1][:top_n]
        return [self.projects[i] for i in top_indices]

    def _format_project_promo(self, projects):
        result = ["Here are some of our most relevant projects:"]
        for proj in projects:
            result.append(
                f"• **{proj['name']}** — {proj['slogan']}\n"
                f"  Industry: {', '.join(proj['industry'])}\n"
                f"  Services: {', '.join(proj['services'])}\n"
                f"  Timeline: {proj['timeline']}\n"
                f"  Description: {proj['description']}\n"
                f"  [View case study]({proj['link']})\n"
            )
        return "\n".join(result)

    def get_response(self, query, model=None, chat_history=None):
        model = model or self.default_model
        lang = self._detect_language(query)
        similar_projects = self._find_similar_projects(query)

        promo_text = self._format_project_promo(similar_projects)

        system_prompt = (
            f"You are a sales assistant at Halo Lab. The user speaks {lang}. "
            f"Your goal is to promote similar projects from our portfolio to convince the client we have experience in their domain. "
            f"Use short, persuasive language. Structure the answer with bullets or paragraphs.\n\n"
            f"USER QUERY: {query}\n\n"
            f"{promo_text}"
        )

        messages = []
        if chat_history:
            messages += chat_history
        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        try:
            import requests
            headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 800
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"
