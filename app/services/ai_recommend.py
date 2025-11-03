from sqlmodel import Session, select
from app.models.room import Room

def recommend_rooms(session: Session, view: str | None, price_max: float | None, capacity: int | None):
    q = select(Room).where(Room.is_active == True)  # noqa: E712
    if view:
        q = q.where(Room.description.ilike(f"%{view}%"))
    if price_max:
        q = q.where(Room.price_per_night <= price_max)
    if capacity:
        q = q.where(Room.capacity >= capacity)
    return session.exec(q).all()
