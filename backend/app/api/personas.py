from fastapi import APIRouter, Query
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def get_personas(
    property_id: int = Query(...)
) -> Dict[str, Any]:
    # Mock response
    return {
        "personas": [
            {"type": "Family", "description": "Families with children, seeking theme parks and pools."},
            {"type": "Couple", "description": "Couples looking for romantic getaways and fine dining."}
        ]
    }
