import os
import requests
from ddgs import DDGS
from lingua import Language, LanguageDetectorBuilder

class CopywriterAgent:
    def __init__(self, default_model="llama3-8b-8192"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.default_model = default_model
        self.language_detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN
        ).build()
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

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

    def _web_search(self, query, max_results=10):
        try:
            with DDGS(timeout=20) as ddgs:
                return list(ddgs.text(query, max_results=max_results))
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def _format_results(self, results):
        if not results:
            return ""
        return "\n".join(
            f"• {self._clean_text(r.get('title', ''))}: {self._clean_text(r.get('body', ''))[:500]}"
            for r in results
        )

    def write_article(self, topic, model=None, chat_history=None):
        model = model or self.default_model
        lang = self._detect_language(topic)
        search_results = self._web_search(topic)
        formatted_results = self._format_results(search_results)

        system_prompt = (
            f"**Task**: Write a comprehensive HTML article on: '{topic}'. "
            f"**Language**: Write in {lang} (same as the topic language).\n"
            "**Format Requirements**:\n"
            "1. Use ONLY HTML5 semantic tags (<article>, <section>, <h1>-<h6>, <p>, <ul>/<ol>, <li>, <blockquote>)\n"
            "2. ABSOLUTELY NO CSS styles, classes or inline styles\n"
            "3. Include at least 3 sections with subtitles\n"
            "4. Structure: Introduction, Main Content, Conclusion\n"
            "5. Use web results as references but rewrite content originally\n\n"
            f"**Reference Materials**:\n{formatted_results}"
        )

        messages = []
        
        # Добавляем историю чата если есть
        if chat_history:
            messages.extend(chat_history)
        
        # Добавляем системный промпт и запрос
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": f"Generate HTML article about: {topic}"})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 4096
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=45
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            error_html = (
                "<article>"
                "<h1>Error Generating Content</h1>"
                "<p>Sorry, I couldn't generate the article. Please try again later.</p>"
                "<p>Technical details: " + str(e)[:200] + "</p>"
                "</article>"
            )
            return error_html
        