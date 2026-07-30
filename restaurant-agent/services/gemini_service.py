import json
import asyncio
from typing import Dict, Any
from config import config
from logger import logger

class GeminiService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client: {e}")

    def generate_content(self, prompt: str) -> str:
        """Generates text from Gemini model synchronously."""
        if not self.client:
            return ""

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for m in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini model '{m}' request failed: {e}")

        return ""

    async def generate_content_async(self, prompt: str) -> str:
        """Generates text from Gemini model asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate_content, prompt)

    def parse_json_response(self, prompt: str) -> Dict[str, Any]:
        """Helper to invoke Gemini and parse JSON response synchronously."""
        text = self.generate_content(prompt)
        return self._clean_and_parse_json(text)

    async def parse_json_async(self, prompt: str) -> Dict[str, Any]:
        """Helper to invoke Gemini and parse JSON response asynchronously."""
        text = await self.generate_content_async(prompt)
        return self._clean_and_parse_json(text)

    def _clean_and_parse_json(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}

        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from Gemini text: {text[:100]}. Error: {e}")
            return {}

gemini_service = GeminiService()
