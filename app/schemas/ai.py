from pydantic import BaseModel
from typing import Optional

class RecommendIn(BaseModel):
    view: Optional[str] = None
    price_max: Optional[float] = None
    capacity: Optional[int] = None
