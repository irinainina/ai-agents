import os
import requests
from ddgs import DDGS
from lingua import Language, LanguageDetectorBuilder

AGENCY_DESCRIPTION = """
Halo Lab are a creative digital agency specializing in web design, development, SEO, testing, and product redesigns.
Halo Lab use modern tools like React.js, Next.js, Vue, Svelte, Tailwind, Node.js, Express, PostgreSQL, MongoDB, Sanity, Prismic, and Webflow.
"""

TONE_INSTRUCTION = """
Be friendly, curious, and helpful.
Appreciate the user's interest, suggest thoughtful ideas, and connect their topic with how our agency could help.
If the topic is even loosely related to web technologies, digital products, online tools, or user experience — naturally offer a relevant service, suggest a creative concept, or ask if they'd like to see examples.
You can also mention potential social, cultural, commercial, or aesthetic value of the proposed idea.
"""

class ResearchAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.default_model = default_model
        self.language_detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN
        ).build()
        if not self.api_key:
            raise ValueError("GROQ_API_KEY required")
        
    def _detect_language(self, text):
        try:
            lang = self.language_detector.detect_language_of(text)
            return lang.iso_code_639_1.name.lower()
        except:
            return "en"

    def _clean_text(self, text):
        if not text:
            return ""
        return " ".join(text.replace('\n', ' ').strip().split())

    def _web_search(self, query, max_results=5):
        try:
            with DDGS(timeout=10) as ddgs:
                return list(ddgs.text(query, max_results=max_results))
        except:
            return []

    def _format_results(self, results):
        if not results:
            return ""
        return "\n".join(
            f"• {self._clean_text(r.get('title', ''))}: {self._clean_text(r.get('body', ''))[:300]}"
            for r in results
        )

    def search_web(self, query, model=None, chat_history=None):
        model = model or self.default_model
        query_language = self._detect_language(query)        
        search_results = self._web_search(query)
        formatted_results = self._format_results(search_results)

        system_prompt = (
            f"You are a Halo Lab Researsh Specialist. Always reply in the user's language (detected: {query_language}).\n"
            f"{AGENCY_DESCRIPTION}\n\n"
            f"{TONE_INSTRUCTION}\n\n"
            f"NEVER include words or phrases in languages other than the user's language (detected as {query_language}), except for terms."
            f"Use web results if they are relevant.\n"
            f"Be clear, helpful, and structured.\n\n"
            f"Web results:\n{formatted_results}"
            f"End with an OPEN question to continue dialogue\n"
            f"Structure response using varied HTML5 semantic tags (<div>, <section>, <h3>-<h6>, <p>, <span>, <ul>/<ol>, <li>, <blockquote>, <strong> etc)\n"
            f"Do NOT begin the response with any heading or title. Start directly with content.\n"
        )

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if chat_history:
            messages += chat_history

        messages.append({"role": "user", "content": query})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 800
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"API error: {str(e)}"
