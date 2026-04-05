import logging
from typing import Optional
import google.generativeai as genai
from core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. AI features will be disabled.")
            self._client = None
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._client = genai.GenerativeModel(settings.GEMINI_MODEL)

    def _is_available(self) -> bool:
        return self._client is not None

    def summarize_tab(
        self,
        title: str,
        url: Optional[str] = None,
        app_name: Optional[str] = None,
    ) -> dict[str, Optional[str]]:
        """
        Generate a short summary and category for a tab or app.

        Returns:
            {"summary": str, "category": str | None}
        """
        if not self._is_available():
            return {"summary": "AI summaries are disabled (no API key).", "category": None}

        context = self._build_context(title, url, app_name)
        prompt = f"""You are a productivity assistant. A user has a browser tab or desktop app open.
Based on the information below, answer in two parts:

1. SUMMARY: One sentence explaining why the user most likely opened this tab/app and what they are trying to accomplish.
2. CATEGORY: One short label categorizing this tab/app (e.g., Work, Entertainment, Shopping, Research, Social, Development, Finance, News, Other).

Tab/App Info:
{context}

Respond in exactly this format:
SUMMARY: <your one-sentence summary>
CATEGORY: <your one-word label>"""

        try:
            response = self._client.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"summary": "Unable to generate summary at this time.", "category": None}

    def _build_context(
        self,
        title: str,
        url: Optional[str],
        app_name: Optional[str],
    ) -> str:
        lines = [f"Title: {title}"]
        if url:
            lines.append(f"URL: {url}")
        if app_name:
            lines.append(f"App Name: {app_name}")
        return "\n".join(lines)

    def _parse_response(self, text: str) -> dict[str, Optional[str]]:
        summary: Optional[str] = None
        category: Optional[str] = None

        for line in text.strip().splitlines():
            line = line.strip()
            if line.upper().startswith("SUMMARY:"):
                summary = line[len("SUMMARY:"):].strip()
            elif line.upper().startswith("CATEGORY:"):
                category = line[len("CATEGORY:"):].strip()

        return {
            "summary": summary or text.strip(),
            "category": category,
        }


# Module-level singleton
gemini_service = GeminiService()
