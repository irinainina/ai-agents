# import os
# import json
import os
import json
import requests
from pathlib import Path
from langdetect import detect, DetectorFactory
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import logging
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DetectorFactory.seed = 0

class ProjectAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.default_model = default_model
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.projects = self._load_projects()
        if not self.projects:
            logger.warning("No projects loaded! Agent will not function properly.")
        
        self.embedder = None
        self.project_embeddings = None
        self.model_name = "paraphrase-MiniLM-L3-v2"

    def _get_embedder(self):
        if self.embedder is None:
            self.embedder = SentenceTransformer(
                self.model_name,
                device="cpu",
                cache_folder="./model_cache"
            )
            logger.info(f"Loaded embedding model: {self.model_name}")
        return self.embedder

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

    def _detect_language(self, text):
        try:
            return detect(text)
        except:
            return "en"

    def _generate_project_embeddings(self):
        if self.project_embeddings is not None:
            return self.project_embeddings
        
        if not self.projects:
            return torch.tensor([])

        embedder = self._get_embedder()
        batch_size = 25
        embeddings = []

        texts = [
            f"{p['name']} {' '.join(p['industry'])} "
            f"{' '.join(p['services'])} {' '.join(p['keywords'])}"
            for p in self.projects
        ]

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_emb = embedder.encode(
                batch_texts,
                convert_to_tensor=True,
                show_progress_bar=False,
                device="cpu",
                normalize_embeddings=True
            )
            embeddings.append(batch_emb.cpu())
            del batch_emb
            gc.collect()

        self.project_embeddings = torch.cat(embeddings, dim=0)
        logger.info(f"Generated embeddings for {len(self.projects)} projects")
        return self.project_embeddings

    def _find_similar_projects(self, query, top_n=3):
        if not self.projects:
            return []

        project_embeddings = self._generate_project_embeddings()
        if project_embeddings.nelement() == 0:
            return []

        query_embedding = self._get_embedder().encode(query, convert_to_tensor=True, normalize_embeddings=True)
        cos_scores = F.cosine_similarity(query_embedding.unsqueeze(0), project_embeddings)
        top_indices = torch.topk(cos_scores, k=top_n).indices
        return [self.projects[i] for i in top_indices]

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

    def get_response(self, query, model=None, chat_history=None):
        model = model or self.default_model
        lang = self._detect_language(query)
        similar_projects = self._find_similar_projects(query)
        promo_text = self._format_project_promo(similar_projects, lang)

        system_prompt = (
            f"You are a sales assistant at Halo Lab. The user speaks {lang}. "
            f"Your goal is to showcase our relevant projects to convince the client we have expertise in their domain.\n\n"
            "Key instructions:\n"
            "1. Start with a confident statement about our experience\n"
            "2. Present 2-3 most relevant projects\n"
            "3. For each project: highlight similarities with client's needs\n"
            "4. Focus on outcomes and benefits, not just features\n"
            "5. End with a call-to-action for next steps\n\n"
            f"CLIENT'S QUERY: {query}\n\n"
            f"RELEVANT PROJECTS:\n{promo_text}"
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
            return "I'm having trouble accessing our project database at the moment. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return "An unexpected error occurred while processing your request."



# import requests
# from pathlib import Path
# from langdetect import detect, DetectorFactory
# import torch
# import torch.nn.functional as F
# from sentence_transformers import SentenceTransformer
# import logging

# # Настройка логирования
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
#         if not self.projects:
#             logger.warning("No projects loaded! Agent will not function properly.")
       
#         self.embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
#         self.project_embeddings = self._generate_project_embeddings()
    
#     def _load_projects(self):
#         """Загружает проекты из файла"""
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
    
#     def _detect_language(self, text):        
#         try:
#             return detect(text)
#         except:
#             return "en"
    
#     def _generate_project_embeddings(self):        
#         if not self.projects:
#             return torch.tensor([])        
        
#         texts = []
#         for proj in self.projects:
#             components = [
#             proj.get('name', ''),
#             ' '.join(proj.get('industry', [])),
#             ' '.join(proj.get('services', [])),
#             ' '.join(proj.get('keywords', []))
#         ]
#             text = " ".join(filter(None, components))
#             texts.append(text)
        
#         return self.embedder.encode(texts, convert_to_tensor=True)
    
#     def _find_similar_projects(self, query, top_n=3):
#         """Находит наиболее релевантные проекты"""
#         if not self.projects or self.project_embeddings.nelement() == 0:
#             return []
        
#         query_embedding = self.embedder.encode(query, convert_to_tensor=True)
       
#         cos_scores = F.cosine_similarity(query_embedding.unsqueeze(0), self.project_embeddings)
#         top_indices = torch.topk(cos_scores, k=top_n).indices
        
#         return [self.projects[i] for i in top_indices]
    
#     def _format_project_promo(self, projects, lang="en"):
#         """Форматирует информацию о проектах для промпта"""
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
#         """Генерирует ответ с рекомендацией проектов"""
#         model = model or self.default_model
#         lang = self._detect_language(query)
#         similar_projects = self._find_similar_projects(query)
#         promo_text = self._format_project_promo(similar_projects, lang)
                
#         system_prompt = (
#             f"You are a sales assistant at Halo Lab. The user speaks {lang}. "
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
#             # return response.json()["choices"][0]["message"]["content"]
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
