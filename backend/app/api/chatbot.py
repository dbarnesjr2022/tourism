from fastapi import APIRouter, Query
from typing import Dict

router = APIRouter()

@router.get("/", response_model=Dict[str, str])
def chatbot_response(
    message: str = Query(...)
) -> Dict[str, str]:
    # Mock response
    return {"response": f"You asked: {message}. Here is a helpful answer!"}
