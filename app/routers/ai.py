from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.ai import RecommendIn
from app.services.ai_recommend import recommend_rooms

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/recommend")
def recommend(payload: RecommendIn, session: Session = Depends(get_session)):
    rooms = recommend_rooms(session, payload.view, payload.price_max, payload.capacity)
    return {"result": [r.dict() for r in rooms]}
