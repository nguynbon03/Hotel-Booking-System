import uuid
from datetime import date
from sqlmodel import SQLModel, Field, Relationship


class DailyPrice(SQLModel, table=True):
    __tablename__ = "daily_prices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rate_plan_id: uuid.UUID = Field(foreign_key="rate_plans.id")

    date: date
    price: float

    rate_plan: "RatePlan" = Relationship(back_populates="daily_prices")
