from sqlmodel import Field
from enum import Enum
from uuid import UUID
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField

from app.models.timestamps import TimeStamps


class JobStatus(str, Enum):
    interviewed = "interviewed"
    declined = "declined"
    pending = "pending"


class Job(TimeStamps, table=True):
    __tablename__ = "jobs"
    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    company: str
    position: str
    createdBy: str = Field(foreign_key="users.username")
    status: JobStatus = Field(default=JobStatus.pending)


class JobBase(BaseModel):
    company: str = Field(max_length=50, min_length=2, pattern=r"^[a-z A-Z]+$")
    position: str = Field(max_length=50, min_length=3, pattern=r"^[a-z A-Z]+$")


class JobUpdate(JobBase):
    company: str | None = Field(
        default=None, max_length=50, min_length=2, pattern=r"^[a-z A-Z]+$"
    )
    position: str | None = Field(
        default=None, max_length=50, min_length=3, pattern=r"^[a-z A-Z]+$"
    )
    status: JobStatus | None = None

