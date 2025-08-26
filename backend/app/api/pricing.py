from fastapi import APIRouter, Query
from typing import Dict, Union

router = APIRouter()

@router.get("/", response_model=Dict[str, Union[str, float]])
def get_pricing(
    property_id: int = Query(...),
    date: str = Query(...)
) -> Dict[str, Union[str, float]]:
    # Mock response
    return {"property_id": property_id, "date": date, "suggested_price": 149.99}
