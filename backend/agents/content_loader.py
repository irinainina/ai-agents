import json
from pathlib import Path

class ContentLoader:
    def __init__(self):
        self.data = {}
        data_dir = Path(__file__).parent.parent / "data"
        
        for file_path in data_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                audience = content["аудитория"]
                self.data[audience] = content

    def get_content(self, audience_type: str, lang: str) -> dict:
        audience_map = {
            "client": "клиенты",
            "designer": "дизайнери",
            "developer": "розробники",
            "guest": "випадковий відвідувач"
        }
        ru_audience = audience_map.get(audience_type, "випадковий відвідувач")
        content = self.data.get(ru_audience, {})
        
        return {
            "key_ideas": content.get("ключевые_идеи", {}).get(lang, []),
            "facts": content.get("факты", []),
            "tone": content.get("язык", ""),
            "style": content.get("стиль_ответов", "")
        }
    