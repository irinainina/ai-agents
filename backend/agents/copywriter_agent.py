import os
import requests
import re
from ddgs import DDGS
from lingua import Language, LanguageDetectorBuilder
from .get_images import get_images

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

    def write_article(self, topic, length=5000, tone="neutral", audience="general public", chat_history=None):
        lang = self._detect_language(topic)
        search_results = self._web_search(topic, max_results=5)
        formatted_results = self._format_results(search_results)

        token_goal = int(length / 4)
        max_tokens = min(8000, token_goal + 1000)

        system_prompt = (
            f"You are a professional copywriter for a Gen-Z audience. Your goal is to entertain and educate."
            f"**Objective**: Create an in-depth HTML article on '{topic}', using the user's language ({lang}).\n"
            f"**Tone Requirements**: Adjust vocabulary, sentence structure, and mood to reflect a {tone} tone. This tone MUST be consistent throughout the article.\n"
            f"**Audience Requirements**: Tailor the content's complexity, references, and examples to match a {audience} audience. Always speak directly to this group.\n"
            f"NEVER include words or phrases in languages other than the user's language (detected as {lang}), except for terms.\n\n"
            f"**Length**: STRICTLY {length} characters (±10%)\n"
            f"**Token Limit**: {max_tokens} tokens\n\n"
            "**Structure Requirements**:\n"
            "1. Start with a summary paragraph.\n"
            "2. Include 3–8 detailed sections with subtitles.\n"
            "3. Use ONLY these HTML tags: <article>, <section>, <h1>-<h6>, <p>, <span>, <ul>, <ol>, <li>, <img>, <blockquote>.\n"
            "4. For EACH image placeholder: Generate EXACTLY 3 English keywords, each a single word, separated by commas inside the comment:\n"
            "   <!--IMAGE_KEYWORDS: keyword1, keyword2-->\n"
            "   <!--IMAGE_HERE-->\n"
            "   Keywords MUST be single words, with no more than 3 total.\n"
            "5. Include 1 or 2 image placeholders (with keywords and image comments) in EACH detailed section.\n"
            "6. End with a conclusion.\n\n"
            f"**Reference Materials**:\n{formatted_results}\n"
            "**Important**:\n"
            "- Keywords MUST be in English\n"
            "- Output ONLY the HTML article"
        )

        user_prompt = (
            f"Generate a full HTML article about: {topic}.\n"
            f"The total length must be approximately {length} characters (±10%).\n"
            f"Use rich details, long sentences, and examples.\n"
            f"Use <!--IMAGE_KEYWORDS: ... --> and <!--IMAGE_HERE--> for image placeholders.\n"
        )

        messages = []
        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=45
            )
            response.raise_for_status()
            html = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return (
                "<article>"
                "<h1>Error Generating Content</h1>"
                "<p>Sorry, I couldn't generate the article. Please try again later.</p>"
                f"<p>Technical details: {str(e)[:200]}</p>"
                "</article>"
            )

        return self._inject_images(html)

    def _inject_images(self, html: str) -> str:        
        pattern = r'<!--IMAGE_KEYWORDS:([^-]+?)-->\s*<!--IMAGE_HERE-->'
        used_urls = set()
        new_html = html
       
        matches = list(re.finditer(pattern, html, re.DOTALL))
        
        for match in matches:
            full_match = match.group(0)
            keywords_str = match.group(1).strip()
         
            keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
            if not keywords:
                continue
                     
            img_options = get_images(keywords, per_page=5) if keywords else []            
           
            selected_url = None
            for url in img_options:
                if url not in used_urls:
                    selected_url = url
                    used_urls.add(url)
                    break
           
            if selected_url:
                img_tag = f'<img src="{selected_url}" width="600" height="400" alt="{keywords_str}">'
                new_html = new_html.replace(full_match, img_tag, 1)
            else:                
                new_html = new_html.replace(full_match, "<!--IMAGE_NOT_FOUND-->", 1)
        
        return new_html
