import os
import json
import requests
from pathlib import Path
from lingua import Language, LanguageDetectorBuilder
import logging
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.default_model = default_model
        self.api_key = os.getenv("GROQ_API_KEY")
        self.language_detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN
        ).build()
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.projects = self._load_projects()
        self.vectorizer, self.tfidf_matrix = self._load_or_generate_tfidf()

    def _load_projects(self):
        data_dir = Path(__file__).parent.parent / "data"
        file_path = data_dir / "projects.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                projects = json.load(f)
                logger.info(f"Successfully loaded {len(projects)} projects")
                return projects
        except FileNotFoundError:
            logger.error(f"Project file not found: {file_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in project file: {file_path}")
        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
        return []

    def _tfidf_cache_path(self):
        return Path(__file__).parent.parent / "data" / "tfidf_cache.pkl"

    def _load_or_generate_tfidf(self):
        cache_path = self._tfidf_cache_path()

        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                logger.info("Loaded cached TF-IDF data")
                return cache_data['vectorizer'], cache_data['matrix']
            except Exception as e:
                logger.warning(f"Failed to load TF-IDF cache: {e}")

        return self._generate_and_cache_tfidf(cache_path)

    def _generate_and_cache_tfidf(self, cache_path):
        if not self.projects:
            return None, None

        texts = [
            f"{p['name']} {' '.join(p['industry'])} "
            f"{' '.join(p['services'])} {' '.join(p['keywords'])}"
            for p in self.projects
        ]

        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            min_df=1
        )

        tfidf_matrix = vectorizer.fit_transform(texts)

        cache_data = {
            'vectorizer': vectorizer,
            'matrix': tfidf_matrix
        }

        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)

        logger.info(f"Generated and cached TF-IDF at {cache_path}")
        return vectorizer, tfidf_matrix

    def _detect_language(self, text):
        try:
            lang = self.language_detector.detect_language_of(text)
            return lang.iso_code_639_1.name.lower()
        except:
            return "en"

    def _find_similar_projects(self, query, top_n=3, exclude_ids=None):
        exclude_ids = set(exclude_ids or [])
        if not self.projects or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        cos_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        sorted_indices = np.argsort(cos_similarities)[::-1]

        selected = []
        for idx in sorted_indices:
            project = self.projects[idx]
            if project["id"] not in exclude_ids:
                selected.append(project)
            if len(selected) == top_n:
                break

        return selected

    def _format_project_promo(self, projects, lang="en"):
        if not projects:
            return "We have extensive experience in this domain. Here are some relevant examples:"

        result = ["Here are some of our most relevant projects:"]
        for idx, proj in enumerate(projects, 1):
            translation_note = " (translated to your language)" if lang != "en" else ""
            result.append(
                f"{idx}. **{proj['name']}**{translation_note}\n"
                f"   - Tagline: {proj['slogan']}\n"
                f"   - Industry: {', '.join(proj['industry'])}\n"
                f"   - Services: {', '.join(proj['services'])}\n"
                f"   - Timeline: {proj['timeline']}\n"
                f"   - Description: {proj['description']}\n"
                f"   - [Case study]({proj['link']})"
            )
        return "\n\n".join(result)

    def get_response(self, query, model=None, chat_history=None, shown_project_ids=None):
        model = model or self.default_model
        lang = self._detect_language(query)
        shown_project_ids = shown_project_ids or []

        similar_projects = self._find_similar_projects(query, exclude_ids=shown_project_ids)
        promo_text = self._format_project_promo(similar_projects, lang)

        system_prompt = (
            f"You are a Sales Manager at Halo Lab. Always reply in the user's language (detected: {lang}).\n"
            f"Translate all content from English to the user's language (detected: {lang}) when responding, except for terms.\n"
            f"Your main goal is to showcase our relevant projects to convince the client we have expertise in their domain.\n\n"
            "Key instructions:\n"
            "1. Start with a confident, warm statement about our experience\n"
            "2. Present 3 most relevant projects\n"
            "3. For each project:\n"
            "– Highlight the problem the client faced and what they wanted to achieve\n"
            "– Show how our solution helped them reach their goals\n"
            "– Emphasize business outcomes and user benefits\n"
            "– Use clear, human language — avoid dry facts, but do not invent details\n"
            "4. Focus on outcomes and benefits, not just features\n"
            "5. Include a call-to-action for next steps\n"
            "6. End with an open question to continue the dialogue\n\n"
            f"CLIENT'S QUERY: {query}\n\n"
            f"RELEVANT PROJECTS:\n{promo_text}\n\n"
            f"NEVER include words or phrases in languages other than the user's language (detected as {lang}), except for terms.\n"
            f"Structure response using varied HTML5 semantic tags (<div>, <section>, <h3>-<h6>, <p>, <span>, <ul>/<ol>, <li>, <blockquote>, <strong> etc)\n"
            f"Do NOT begin the response with any heading or title. Start directly with content.\n"
        )

        messages = [{"role": "system", "content": system_prompt}]
        if chat_history:
            filtered_history = [msg for msg in chat_history if msg["role"] != "system"]
            messages.extend(filtered_history)
        messages.append({"role": "user", "content": query})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1000,
            "top_p": 0.9
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )
            response.raise_for_status()
            return {
                "text": response.json()["choices"][0]["message"]["content"],
                "project_ids": [p["id"] for p in similar_projects]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"text": "I'm having trouble accessing our project database at the moment. Please try again later."}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"text": "An unexpected error occurred while processing your request."}



# import os
# import json
# import requests
# from pathlib import Path
# from langdetect import detect, DetectorFactory
# import torch
# import torch.nn.functional as F
# from sentence_transformers import SentenceTransformer
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# DetectorFactory.seed = 0

# class ProjectAgent:
#     def __init__(self, default_model="llama3-8b-8192"):
#         self.default_model = default_model
#         self.api_key = os.getenv("GROQ_API_KEY")
#         if not self.api_key:
#             raise ValueError("GROQ_API_KEY environment variable not set")
        
#         self.projects = self._load_projects()
#         self.embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2", device="cpu")
#         self.project_embeddings = self._load_or_generate_embeddings()

#     def _load_projects(self):
#         data_dir = Path(__file__).parent.parent / "data"
#         file_path = data_dir / "projects.json"
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 projects = json.load(f)
#                 logger.info(f"Successfully loaded {len(projects)} projects")
#                 return projects
#         except FileNotFoundError:
#             logger.error(f"Project file not found: {file_path}")
#         except json.JSONDecodeError:
#             logger.error(f"Invalid JSON in project file: {file_path}")
#         except Exception as e:
#             logger.error(f"Error loading projects: {str(e)}")
#         return []

#     def _embedding_cache_path(self):
#         return Path(__file__).parent.parent / "data" / "project_embeddings.pt"

#     def _load_or_generate_embeddings(self):
#         cache_path = self._embedding_cache_path()

#         if cache_path.exists():
#             try:
#                 embeddings = torch.load(cache_path, map_location="cpu")
#                 logger.info("Loaded cached project embeddings")
#                 return embeddings
#             except Exception as e:
#                 logger.warning(f"Failed to load cached embeddings: {e}")

#         return self._generate_and_cache_embeddings(cache_path)

#     def _generate_and_cache_embeddings(self, cache_path):
#         if not self.projects:
#             return torch.tensor([])

#         texts = [
#             f"{p['name']} {' '.join(p['industry'])} "
#             f"{' '.join(p['services'])} {' '.join(p['keywords'])}"
#             for p in self.projects
#         ]

#         embeddings = self.embedder.encode(
#             texts,
#             convert_to_tensor=True,
#             normalize_embeddings=True
#         )

#         torch.save(embeddings, cache_path)
#         logger.info(f"Generated and cached embeddings at {cache_path}")
#         return embeddings

#     def _detect_language(self, text):
#         try:
#             return detect(text)
#         except:
#             return "en"

#     def _find_similar_projects(self, query, top_n=3):
#         if not self.projects or self.project_embeddings.nelement() == 0:
#             return []

#         query_embedding = self.embedder.encode(
#             query,
#             convert_to_tensor=True,
#             normalize_embeddings=True
#         )

#         cos_scores = F.cosine_similarity(query_embedding.unsqueeze(0), self.project_embeddings)
#         top_indices = torch.topk(cos_scores, k=top_n).indices
#         return [self.projects[i] for i in top_indices]

#     def _format_project_promo(self, projects, lang="en"):
#         if not projects:
#             return "We have extensive experience in this domain. Here are some relevant examples:"

#         result = ["Here are some of our most relevant projects:"]
#         for idx, proj in enumerate(projects, 1):
#             translation_note = " (translated to your language)" if lang != "en" else ""
#             result.append(
#                 f"{idx}. **{proj['name']}**{translation_note}\n"
#                 f"   - Tagline: {proj['slogan']}\n"
#                 f"   - Industry: {', '.join(proj['industry'])}\n"
#                 f"   - Services: {', '.join(proj['services'])}\n"
#                 f"   - Timeline: {proj['timeline']}\n"
#                 f"   - Description: {proj['description']}\n"
#                 f"   - [Case study]({proj['link']})"
#             )
#         return "\n\n".join(result)

#     def get_response(self, query, model=None, chat_history=None):
#         model = model or self.default_model
#         lang = self._detect_language(query)
#         similar_projects = self._find_similar_projects(query)
#         promo_text = self._format_project_promo(similar_projects, lang)

#         system_prompt = (
#             f"You are a sales assistant at Halo Lab. The user speaks {lang}. "
#             f"Answer the user in the same language they use ({lang}). "
#             f"Your goal is to showcase our relevant projects to convince the client we have expertise in their domain.\n\n"
#             "Key instructions:\n"
#             "1. Start with a confident statement about our experience\n"
#             "2. Present 2-3 most relevant projects\n"
#             "3. For each project: highlight similarities with client's needs\n"
#             "4. Focus on outcomes and benefits, not just features\n"
#             "5. End with a call-to-action for next steps\n\n"
#             f"CLIENT'S QUERY: {query}\n\n"
#             f"RELEVANT PROJECTS:\n{promo_text}"
#         )

#         messages = [{"role": "system", "content": system_prompt}]
#         if chat_history:
#             filtered_history = [msg for msg in chat_history if msg["role"] != "system"]
#             messages.extend(filtered_history)
#         messages.append({"role": "user", "content": query})

#         headers = {"Authorization": f"Bearer {self.api_key}"}
#         payload = {
#             "model": model,
#             "messages": messages,
#             "temperature": 0.6,
#             "max_tokens": 1000,
#             "top_p": 0.9
#         }

#         try:
#             response = requests.post(
#                 "https://api.groq.com/openai/v1/chat/completions",
#                 headers=headers,
#                 json=payload,
#                 timeout=25
#             )
#             response.raise_for_status()
#             return {
#                 "text": response.json()["choices"][0]["message"]["content"],
#                 "project_ids": [p["id"] for p in similar_projects]
#             }
#         except requests.exceptions.RequestException as e:
#             logger.error(f"API request failed: {str(e)}")
#             return "I'm having trouble accessing our project database at the moment. Please try again later."
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return "An unexpected error occurred while processing your request."
        