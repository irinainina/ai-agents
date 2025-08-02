import os
import json
import requests
from pathlib import Path
from lingua import Language, LanguageDetectorBuilder

class WelcomeAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.default_model = default_model
        self.language_detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN
        ).build()
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.company_data = self._load_company_data()

    def _load_company_data(self):
        data_dir = Path(__file__).parent.parent / "data"
        file_path = data_dir / "welcome.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading company data: {e}")
            return {}

    def _detect_language(self, text):
        try:
            lang = self.language_detector.detect_language_of(text)
            return lang.iso_code_639_1.name.lower()
        except:
            return "en"

    def _format_audience_info(self, audience_type):
        """Format audience-specific information for the prompt"""
        if not audience_type or audience_type not in self.company_data:
            return ""
            
        audience_data = self.company_data[audience_type]
        parts = [
            f"# {audience_type.upper()} INFORMATION",
            f"Intro: {audience_data['intro']}"
        ]
        
        parts.append("\nKey Points:")
        for point in audience_data["key_points"]:
            parts.append(f"- {point}")
            
        parts.append("\nServices:")
        for service in audience_data["services"]:
            parts.append(f"- {service}")
            
        parts.append("\nAchievements:")
        for achievement in audience_data["achievements"]:
            parts.append(f"- {achievement}")
        
        return "\n".join(parts)

    def _format_key_facts(self, audience_type):
        """Format key facts as bullet points for prompting"""
        if audience_type not in self.company_data:
            return "- General company information"
        
        data = self.company_data[audience_type]
        facts = data.get("key_points", []) + data.get("achievements", [])
        return "\n".join([f"- {fact}" for fact in facts[:6]])

    def _get_mentioned_facts(self, chat_history):
        """Extract already mentioned facts from conversation history"""
        if not chat_history:
            return "None"
        
        mentioned = set()
        for msg in chat_history:
            if msg["role"] == "assistant":
                content = msg["content"].lower()
                # Check against all possible facts
                for audience in self.company_data.values():
                    for fact in audience.get("key_points", []) + audience.get("achievements", []):
                        if any(word in content for word in fact.lower().split()[:3]):      mentioned.add(fact)
        
        return ", ".join(list(mentioned)[:5]) + ("..." if len(mentioned) > 5 else "")
    
    def get_response(self, query, model=None, chat_history=None):
        model = model or self.default_model
        lang = self._detect_language(query)
        
        audience_type = self._detect_audience_type(query, lang)
        audience_info = self._format_audience_info(audience_type)
        
        system_prompt = (
            f"You are a Halo Lab PR Specialist. Respond in the user's language (detected: {lang}). "
            "Translate all content from English to the user's language when responding, except for terms and proper nouns.\n\n"

            "PRIMARY OBJECTIVE:\n"
            "1. Your highest priority is to form a positive impression of Halo Lab and build trust with the user.\n"
            "2. Show empathy, curiosity, and genuine interest in their goals.\n"
            "3. Your role is not only to answer — but to attract, inspire, and guide the user toward working with us.\n"
            "Always maintain a respectful, polite, and friendly tone. Acknowledge the value of the user's input and emphasize their importance in the conversation.\n"
            "5. Even if their technologies, approaches or views differs from ours, find common ground and demonstrate how we can still deliver great results.\n\n"
            
            "STRICT GUIDELINES:\n"
            "1. NEVER repeat the same facts or phrases consecutively\n"
            "2. NEVER use generic politeness formulas or stock phrases. Start directly with context-relevant content.\n"
            "3. Vary your responses - each answer should feel fresh and contextual\n"
            "4. Explicitly validate the user's perspective. If they share concerns or criticism, respond with appreciation for their honesty before addressing the point.\n"
            "5. NEVER include words or phrases in languages other than the user's language (detected as {lang}), except for terms and proper nouns.\n\n"
            
            "CONTENT RULES:\n"
            "1. Prioritize these company facts for {audience_type}:\n"
            f"{self._format_key_facts(audience_type)}\n"
            "2. Include 2-4 most relevant facts per response\n"
            "3. Do not invent facts about Halo Lab, but feel free to engage with user's input using general knowledge and a friendly tone.\n"
            "4. Keep responses concise\n\n"
            
            "CONVERSATION FLOW:\n"
            "1. Answer the current question directly\n"
            "2. Add relevant facts not previously mentioned\n"
            "3. Provide context or example where appropriate\n"
            "4. End with an OPEN question to continue dialogue\n"
            "5. Structure response using varied HTML5 semantic tags (<div>, <section>, <h3>-<h6>, <p>, <span>, <ul>/<ol>, <li>, <blockquote>, <strong> etc)\n"
            "2. ABSOLUTELY NO CSS styles, classes or inline styles\n"
            
            "COMPANY FACTS:\n"
            "════════════════════════════\n"
            f"{audience_info}\n"
            "════════════════════════════\n\n"
            
            f"Previous facts mentioned: {self._get_mentioned_facts(chat_history)}"
        )


        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            messages += chat_history
            
        messages.append({"role": "user", "content": query})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 800,
            "top_p": 0.95
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _detect_audience_type(self, query, lang):
        """Detect audience type using LLM classification"""
        prompt = (
            f"Classify the user type based on this message: '{query}'\n"
            "Options: client, designer, developer, other\n"
            "Respond ONLY with the single most relevant audience type."
        )
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "max_tokens": 15
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"].lower()
            
            for audience in ["client", "designer", "developer"]:
                if audience in result:
                    return audience
            return "other"
        except:
            return "other"
        



# import os
# import json
# import requests
# from pathlib import Path
# from lingua import Language, LanguageDetectorBuilder

# class WelcomeAgent:
#     def __init__(self, default_model="llama3-8b-8192"):
#         self.api_key = os.getenv("GROQ_API_KEY")
#         self.default_model = default_model
#         self.language_detector = LanguageDetectorBuilder.from_languages(
#             Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN
#         ).build()
#         if not self.api_key:
#             raise ValueError("GROQ_API_KEY environment variable not set")
#         self.company_data = self._load_company_data()

#     def _load_company_data(self):
#         data_dir = Path(__file__).parent.parent / "data"
#         file_path = data_dir / "welcome.json"
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception as e:
#             print(f"Error loading company data: {e}")
#             return {}

#     def _detect_language(self, text):
#         try:
#             lang = self.language_detector.detect_language_of(text)
#             return lang.iso_code_639_1.name.lower()
#         except:
#             return "en"

#     def _format_audience_info(self, audience_type):
#         """Format audience-specific information for the prompt"""
#         if not audience_type or audience_type not in self.company_data:
#             return ""
            
#         audience_data = self.company_data[audience_type]
#         parts = [
#             f"# {audience_type.upper()} INFORMATION",
#             f"Intro: {audience_data['intro']}"
#         ]
        
#         parts.append("\nKey Points:")
#         for point in audience_data["key_points"]:
#             parts.append(f"- {point}")
            
#         parts.append("\nServices:")
#         for service in audience_data["services"]:
#             parts.append(f"- {service}")
            
#         parts.append("\nAchievements:")
#         for achievement in audience_data["achievements"]:
#             parts.append(f"- {achievement}")
        
#         return "\n".join(parts)

#     def get_response(self, query, model=None, chat_history=None):
#         model = model or self.default_model
#         lang = self._detect_language(query)
        
#         audience_type = self._detect_audience_type(query, lang)
#         audience_info = self._format_audience_info(audience_type)
        
#         system_prompt = (
#             f"You are a Halo Lab assistant. Respond in the user's language (detected: {lang}). "
#             "Translate all content from English to the user's language when responding, except for proper nouns (company names, technology names).\n\n"
            
#             "Follow these steps:\n"
#             "1. Identify user type (client/designer/developer/other) from their message\n"
#             "2. Always include the relevant information below for that audience type in your answer\n"
#             "   (you may also add general context if needed to fully answer the question)\n"
#             "3. Include specific facts, numbers, and service names where available\n"
#             "4. Keep responses concise (1–2 paragraphs), structured and professional\n"
#             "5. Never invent facts about the company\n\n"

#             "COMPANY INFORMATION:\n"
#             "════════════════════════════\n"
#             f"{audience_info}\n"
#             "════════════════════════════\n\n"

#             f"User type: {audience_type or 'other'} — include relevant company facts for this audience."
#         )


#         messages = [{"role": "system", "content": system_prompt}]
        
#         if chat_history:
#             messages += chat_history
            
#         messages.append({"role": "user", "content": query})

#         headers = {"Authorization": f"Bearer {self.api_key}"}
#         payload = {
#             "model": model,
#             "messages": messages,
#             "temperature": 0.5,
#             "max_tokens": 600,
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
#             return response.json()["choices"][0]["message"]["content"]
#         except Exception as e:
#             return f"Error: {str(e)}"
    
#     def _detect_audience_type(self, query, lang):
#         """Detect audience type using LLM classification"""
#         prompt = (
#             f"Classify the user type based on this message: '{query}'\n"
#             "Options: client, designer, developer, other\n"
#             "Respond ONLY with the single most relevant audience type."
#         )
        
#         headers = {"Authorization": f"Bearer {self.api_key}"}
#         payload = {
#             "model": "llama3-8b-8192",
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.6,
#             "max_tokens": 15
#         }

#         try:
#             response = requests.post(
#                 "https://api.groq.com/openai/v1/chat/completions",
#                 headers=headers,
#                 json=payload,
#                 timeout=10
#             )
#             response.raise_for_status()
#             result = response.json()["choices"][0]["message"]["content"].lower()
            
#             for audience in ["client", "designer", "developer"]:
#                 if audience in result:
#                     return audience
#             return "other"
#         except:
#             return "other"
        