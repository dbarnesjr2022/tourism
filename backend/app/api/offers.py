from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any, Dict, cast
from pydantic import BaseModel, Field, ConfigDict
from app.models.user import User
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.offer import Offer
from app.api.auth import get_current_user

# router prefix is provided in main.py via include_router(..., prefix="/offers")
router = APIRouter(tags=["offers"])


class OfferCreate(BaseModel):
    title: str
    description: str | None = None
    businesses: List[int] = Field(default_factory=list)  # list of business ids participating


class OfferOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    businesses: List[int] = Field(default_factory=list)
    predicted_uplift: float | None = None
    # Pydantic v2: use ConfigDict and from_attributes to allow ORM objects
    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=OfferOut)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> OfferOut:
    # Simple mock: predicted uplift = 0.05 * number of businesses
    # basic input validation
    if not payload.title or len(payload.title.strip()) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title must be at least 3 characters")
    if len(payload.businesses) > 50:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="too many businesses in offer")
    # payload.businesses is List[int] per Pydantic; just check positivity
    if any(b <= 0 for b in payload.businesses):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="business ids must be positive integers")

    predicted = 0.05 * max(1, len(payload.businesses))
    offer = Offer(title=payload.title, description=payload.description,
                  businesses=','.join(str(b) for b in payload.businesses),
                  predicted_uplift=predicted)
    db.add(offer)
    try:
        db.commit()
        db.refresh(offer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    # parse businesses back to list for response
    # build response dict explicitly to avoid deprecated from_orm
    # get concrete values for static analysis using getattr + cast
    id_val = cast(int, getattr(offer, "id"))
    title_val = cast(str, getattr(offer, "title"))
    desc_val = getattr(offer, "description", None)
    businesses_val = [int(x) for x in (getattr(offer, "businesses", "") or "").split(',') if x]
    pred_val = cast(float | None, getattr(offer, "predicted_uplift", None))

    resp: Dict[str, Any] = {
        "id": id_val,
        "title": title_val,
        "description": desc_val,
        "businesses": businesses_val,
        "predicted_uplift": pred_val,
    }
    return OfferOut.model_validate(resp)


@router.get("/", response_model=List[OfferOut])
def list_offers(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> List[OfferOut]:
    offers = db.query(Offer).order_by(Offer.created_at.desc()).all()
    results: List[OfferOut] = []
    for o in offers:
        id_val = cast(int, getattr(o, "id"))
        title_val = cast(str, getattr(o, "title"))
        desc_val = getattr(o, "description", None)
        businesses_val = [int(x) for x in (getattr(o, "businesses", "") or "").split(',') if x]
        pred = cast(float | None, getattr(o, "predicted_uplift", None))

        resp: Dict[str, Any] = {
            "id": id_val,
            "title": title_val,
            "description": desc_val,
            "businesses": businesses_val,
            "predicted_uplift": pred,
        }
        results.append(OfferOut.model_validate(resp))
    return results
