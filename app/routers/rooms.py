from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.redis import get_cache, set_cache, delete_cache
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("", response_model=list[RoomOut])
def list_rooms(session: Session = Depends(get_session)):
    if cached := get_cache("rooms:all"):
        import json
        return [RoomOut(**x) for x in json.loads(cached)]
    rooms = session.exec(select(Room).where(Room.is_active == True)).all()  # noqa: E712
    import json
    set_cache("rooms:all", json.dumps([r.dict() for r in rooms]), ttl=60)
    return rooms

@router.post("", response_model=RoomOut)
def create_room(payload: RoomCreate, session: Session = Depends(get_session)):
    room = Room(**payload.dict())
    session.add(room); session.commit(); session.refresh(room)
    delete_cache("rooms:all")
    return room
