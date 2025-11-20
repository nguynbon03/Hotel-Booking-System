from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class EmailToken(SQLModel, table=True):
    """
    Stores temporary email-based tokens for verification or password reset.

    Attributes:
        user_id: References the user this token belongs to.
        code: The verification or reset code.
        expires_at: Timestamp when the code becomes invalid.
        type: Either 'verify' or 'reset' to distinguish usage.
        created_at: When the token was created.
    """
    __tablename__ = "email_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    code: str
    expires_at: datetime
    type: str  # "verify" or "reset"
    created_at: datetime = Field(default_factory=datetime.utcnow)
