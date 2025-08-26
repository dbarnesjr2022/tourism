from fastapi import APIRouter, Query
from typing import List, Dict, Union
from app.services.forecast import predict_demand

router = APIRouter()

@router.get("/", response_model=Dict[str, List[Dict[str, Union[str, int]]]])
def get_forecast(
    start_date: str = Query(...),
    end_date: str = Query(...),
    property_id: int = Query(...)
) -> Dict[str, List[Dict[str, Union[str, int]]]]:
    forecast: List[Dict[str, Union[str, int]]] = predict_demand(start_date, end_date, property_id)
    return {"forecast": forecast}
