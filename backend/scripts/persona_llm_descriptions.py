"""
Persona LLM Description Generator

- Loads clustered personas from persona_clusters.json
- Uses OpenAI GPT (or Claude API) to generate persona descriptions
- Outputs enriched persona data with LLM-generated descriptions
- Designed for dashboard and campaign integration
"""
import json
from typing import Dict, Any
import os
import openai


INPUT_PATH = os.path.join(os.path.dirname(__file__), "persona_clusters.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "persona_llm_descriptions.json")

# Do NOT hard-code API keys. Read from the environment only.
# Ensure OPENAI_API_KEY is set in your environment or CI secrets.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def generate_description(persona: Dict[str, Any]) -> str:
    """
    Generate a persona description using OpenAI GPT-4 API.
    """
    prompt = (
        f"You are an expert in travel and hospitality marketing. "
        f"Given the following persona data, write a detailed, engaging description for use in a dashboard and marketing campaigns.\n"
        f"Persona data: {json.dumps(persona, ensure_ascii=False)}\n"
        f"Description:"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a travel marketing expert."},
                      {"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.7
        )
        # For openai>=1.0.0, use response.choices[0].message.content or response.choices[0].content
        # Try both, fallback if needed
        # Try to extract the content from the response in a robust way
        choice = response.choices[0]
        content = None
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            content = getattr(choice.message, 'content', None)
        elif hasattr(choice, 'content'):
            content = getattr(choice, 'content', None)
        if isinstance(content, str):
            return content.strip()
        return "[Error: Unexpected OpenAI response format]"
    except Exception as e:
        return f"[Error generating description: {e}]"



def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)["data"]
    enriched: list[Dict[str, Any]] = []
    for persona in data:
        desc = generate_description(persona)
        persona["llm_description"] = desc
        enriched.append(persona)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f"Saved LLM persona descriptions to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
