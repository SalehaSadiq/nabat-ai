import json, os
from typing import Any

class LLMService:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        try:
            import streamlit as st
            self.api_key = st.secrets.get("OPENAI_API_KEY", self.api_key)
            self.model = st.secrets.get("OPENAI_MODEL", self.model)
        except Exception: pass

    @property
    def available(self): return bool(self.api_key)

    def json_call(self, system: str, payload: Any, fallback: dict, image_data_url: str | None = None) -> dict:
        if not self.available: return fallback
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            content = [{"type":"text", "text":json.dumps(payload, ensure_ascii=False, default=str)}]
            if image_data_url: content.append({"type":"image_url", "image_url":{"url":image_data_url}})
            for _ in range(2):
                r = client.chat.completions.create(model=self.model, response_format={"type":"json_object"},
                    messages=[{"role":"system","content":system},{"role":"user","content":content}], temperature=0.2)
                try: return json.loads(r.choices[0].message.content)
                except Exception: continue
        except Exception: pass
        return fallback
