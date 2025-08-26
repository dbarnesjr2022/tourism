"""
LLM Campaign Content Generator

- Loads persona data from persona_llm_descriptions.json
- Uses OpenAI GPT-4 to generate campaign copy (email, social, postcard)
- Outputs enriched campaign data for dashboard and delivery
"""
import json
import os
from typing import Dict, Any, List, Optional
import openai

INPUT_PATH = os.path.join(os.path.dirname(__file__), "persona_llm_descriptions.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "campaign_llm_content.json")

# Do NOT hard-code API keys. Read from the environment only.
# Ensure OPENAI_API_KEY is set in your environment or CI secrets.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_campaign_content(persona: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate campaign copy for email, social, and postcard using OpenAI GPT-4.
    """
    results: Dict[str, str] = {}
    for channel in ["email", "social", "postcard"]:
        prompt = (
            f"You are a travel marketing expert. Given the following persona, write a compelling {channel} campaign copy. "
            f"Persona: {json.dumps(persona, ensure_ascii=False)}\n"
            f"Copy:"
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a travel marketing expert."},
                          {"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.7
            )
            choice: Any = response.choices[0]
            content: Optional[str] = None
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = getattr(choice.message, 'content', None)
            elif hasattr(choice, 'content'):
                content = getattr(choice, 'content', None)
            if isinstance(content, str):
                results[channel] = content.strip()
            else:
                results[channel] = f"[Error: Unexpected OpenAI response format]"
        except Exception as e:
            results[channel] = f"[Error generating {channel} copy: {e}]"
    return results  # type: Dict[str, str]

def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        personas: List[Dict[str, Any]] = json.load(f)
    campaigns: List[Dict[str, Any]] = []
    for persona in personas:
        campaign_content: Dict[str, str] = generate_campaign_content(persona)
        persona["campaign_content"] = campaign_content
        campaigns.append(persona)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)
    print(f"Saved LLM campaign content to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
