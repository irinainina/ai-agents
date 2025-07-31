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

    def get_response(self, query, model=None, chat_history=None):
        model = model or self.default_model
        lang = self._detect_language(query)
        
        audience_type = self._detect_audience_type(query, lang)
        audience_info = self._format_audience_info(audience_type)
        
        system_prompt = (
            f"You are a Halo Lab assistant. Respond in the user's language (detected: {lang}). Translate all content from English to the user's language when responding, except for proper nouns (company names, technology names).\n\n"
            "Follow these steps:\n"
            "1. Identify user type (client/designer/developer/other) from their message\n"
            "2. Use ONLY the relevant information below for that audience type\n"
            "3. Include specific facts, numbers and service names where available\n"
            "4. Keep responses concise (1-2 paragraphs), structured and professional\n"
            "5. Never invent information!\n\n"
            "COMPANY INFORMATION:\n"
            "════════════════════════════\n"
            f"{audience_info}\n"
            "════════════════════════════\n\n"
            f"Detected audience type: {audience_type or 'other'}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            messages += chat_history
            
        messages.append({"role": "user", "content": query})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 600,
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
        