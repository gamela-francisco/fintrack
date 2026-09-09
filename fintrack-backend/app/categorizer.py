from dotenv import load_dotenv
load_dotenv()

import os
import httpx


class OllamaCategorizer:
    async def categorize(self, description: str) -> str:
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        base_url = base_url.rstrip("/")
        url = f"{base_url}/api/generate"

        prompt = (
            f"Categorize the following description into a single, most relevant category word."
            f"Return only the category word, nothing else. No punctuation needed. Description: {description}"
        )

        payload = {
            "model": os.getenv("LLM_MODEL", "llama3.2"),
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            category = data.get("response", "").strip()
            return category