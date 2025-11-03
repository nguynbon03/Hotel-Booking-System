from pydantic import BaseModel

class ChatIn(BaseModel):
    room: str
    message: str
