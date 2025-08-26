from fastapi import APIRouter, Query
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def get_campaigns(
    persona_type: str = Query(...)
) -> Dict[str, Any]:
    # Mock response
    return {
        "persona_type": persona_type,
        "campaign": {
            "email": f"Special offer for {persona_type}!",
            "social": f"Don't miss out, {persona_type}s!",
            "postcard": f"Greetings from Orlando for {persona_type}s!"
        }
    }
