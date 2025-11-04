from datetime import datetime
from sqlmodel import SQLModel, Field

class TimeStamps(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
